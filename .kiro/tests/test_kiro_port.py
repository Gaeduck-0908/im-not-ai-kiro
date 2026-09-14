"""Kiro configuration, installed runtime, migration and provenance contracts."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("kiro_installer", ROOT / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class ProvenanceTests(unittest.TestCase):
    def test_imported_files_match_pinned_upstream_blobs(self):
        manifest = json.loads((ROOT / "UPSTREAM.json").read_text(encoding="utf-8"))
        for item in manifest["files"]:
            with self.subTest(path=item["path"]):
                data = (ROOT / item["path"]).read_bytes()
                blob = b"blob " + str(len(data)).encode() + b"\0" + data
                self.assertEqual(hashlib.sha1(blob).hexdigest(), item["blob_sha"])

    def test_source_config_paths_and_role_allowlist(self):
        agents = ROOT / ".kiro/agents"
        self.assertEqual({p.stem for p in agents.glob("*.json")}, set(installer.ROLES))
        for path in agents.glob("*.json"):
            config = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue((agents / config["prompt"].removeprefix("file://")).is_file())
            self.assertNotIn("model", config)
            for resource in config["resources"]:
                self.assertTrue((ROOT / resource.removeprefix("file://")).is_file())
        main = json.loads((agents / "humanize-korean.json").read_text(encoding="utf-8"))
        self.assertEqual(set(main["toolsSettings"]["subagent"]["availableAgents"]), set(installer.ROLES) - {"humanize-korean"})
        self.assertIn("shell", main["tools"])
        self.assertNotIn("shell", main["allowedTools"])

    def test_chunk_outputs_and_optional_diagnosis_are_explicit(self):
        skill = (ROOT / ".kiro/skills/humanize-korean/SKILL.md").read_text(encoding="utf-8")
        monolith = (ROOT / ".kiro/prompts/humanize-monolith.txt").read_text(encoding="utf-8")
        finalizer = (ROOT / ".kiro/prompts/humanize-finalizer.txt").read_text(encoding="utf-8")
        self.assertIn("`output_path`(**필수**)", monolith)
        self.assertIn("body_only", monolith)
        self.assertIn("body 청크가 하나여도", skill)
        self.assertIn("항상 재조립", skill)
        self.assertIn("`diagnosis_path`(**선택**)", finalizer)
        self.assertIn("00_metrics.error", skill)
        for text in (skill, monolith, finalizer):
            self.assertNotIn("CLAUDE_SKILL_DIR", text)
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", text)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.home = self.base / "한글 & user's kiro"

    def run_install(self, *args):
        return installer.main(["--kiro-home", str(self.home), *args])

    def test_dry_run_does_not_create_destination(self):
        self.assertEqual(self.run_install("--dry-run"), 0)
        self.assertFalse(self.home.exists())

    def test_install_cannot_retire_source_checkout_files(self):
        with self.assertRaises(ValueError):
            installer.main(["--kiro-home", str(ROOT / ".kiro")])
        self.assertTrue((ROOT / ".kiro/skills/humanize-korean/SKILL.md").is_file())

    def test_install_resolves_all_paths_and_excludes_tests(self):
        self.assertEqual(self.run_install(), 0)
        runtime = self.home / installer.PACKAGE
        for name in installer.ROLES:
            config = json.loads((self.home / "agents" / f"{name}.json").read_text(encoding="utf-8"))
            for uri in [config["prompt"], *config["resources"]]:
                path = Path(uri.removeprefix("file://"))
                self.assertTrue(path.is_absolute())
                self.assertTrue(path.is_file())
                self.assertNotIn("__HUMANIZE_ROOT__", path.read_text(encoding="utf-8"))
        self.assertTrue((runtime / "LICENSE").is_file())
        self.assertFalse((runtime / "tests").exists())
        self.assertFalse(list(runtime.rglob("*.pyc")))

    def test_reinstall_is_idempotent(self):
        self.run_install()
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.home.rglob("*") if p.is_file()}
        self.run_install()
        after = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.home.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertFalse((self.home / "backups").exists())

    def test_upgrade_backs_up_owned_files_and_preserves_other_agents(self):
        owned = self.home / "agents/humanize-korean.json"
        retired = self.home / "agents/ai-tell-detector.json"
        unrelated = self.home / "agents/humanize-custom.json"
        old_skill = self.home / "skills/humanize-korean/SKILL.md"
        custom_rule = old_skill.parent / "my-rules.md"
        for path in (owned, retired, unrelated, old_skill, custom_rule):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("customized old content", encoding="utf-8")
        self.run_install()
        self.assertFalse(retired.exists())
        self.assertFalse(old_skill.exists())
        for path in (unrelated, custom_rule):
            self.assertEqual(path.read_text(), "customized old content")
        backup, = (self.home / "backups" / installer.PACKAGE).iterdir()
        for path in (owned, retired, old_skill):
            self.assertEqual((backup / path.relative_to(self.home)).read_text(), "customized old content")

    def test_redirected_install_is_rejected_before_mutation(self):
        self.home.mkdir()
        outside = self.base / "outside"
        outside.mkdir()
        try:
            (self.home / "agents").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Creating symlinks requires OS permission")
        with self.assertRaises(ValueError):
            self.run_install()
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.home / installer.PACKAGE).exists())

    def test_runtime_operates_from_unrelated_cwd_without_source_tests(self):
        self.run_install()
        runtime = self.home / installer.PACKAGE
        cwd = self.base / "작업 폴더"
        run = cwd / "_workspace/example"
        run.mkdir(parents=True)
        original = "정부는 예산을 늘려야 한다. 참여자는 1,200명이다."
        (run / "01_input.txt").write_text(original, encoding="utf-8")
        env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}

        def invoke(name, *args):
            return subprocess.run([sys.executable, str(runtime / "scripts" / name), *args], cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", timeout=30)

        result = invoke("prepare_monolith_input.py", "--run-dir", "_workspace/example", "--genre", "report")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((run / "00_metrics.error").exists())
        metrics = json.loads((run / "00_metrics.json").read_text(encoding="utf-8"))
        self.assertIn(metrics["route_hint"], ("light", "standard", "heavy"))
        self.assertFalse((runtime / "_workspace").exists())
        (run / "final.md").write_text(original, encoding="utf-8")
        flags = ("--before", "_workspace/example/01_input.txt", "--after", "_workspace/example/final.md")
        result = invoke("verify_gates.py", *flags)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("[P3 golden] PASS", result.stdout)
        (run / "final.md").write_text(original + " 예산은 3.5조 원이다.", encoding="utf-8")
        result = invoke("verify_gates.py", *flags)
        self.assertIn(result.returncode, (1, 2), result.stdout)
        self.assertIn("number_injected", result.stdout)
        result = invoke("verify_gates.py", "--before", "missing.txt", "--after", "missing.md")
        self.assertEqual(result.returncode, 3)


if __name__ == "__main__":
    unittest.main()
