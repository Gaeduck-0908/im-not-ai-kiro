#!/usr/bin/env python3
"""Install only this port's files; back up replaced and retired files."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile

SOURCE = Path(__file__).resolve().parent
PACKAGE = "im-not-ai-kiro"
ROLES = ("humanize-korean", "humanize-monolith", "humanize-diagnostician", "humanize-finalizer")
LEGACY = ("ai-tell-detector", "korean-style-rewriter", "content-fidelity-auditor", "naturalness-reviewer")


def install_plan(kiro_home: Path) -> tuple[dict[Path, bytes], list[Path]]:
    runtime = kiro_home / PACKAGE
    replacements = {}
    for folder in ("scripts", "prompts", "skills/humanize-korean"):
        for source in sorted((SOURCE / ".kiro" / folder).rglob("*")):
            if not source.is_file() or "__pycache__" in source.parts or source.suffix == ".pyc":
                continue
            relative = source.relative_to(SOURCE / ".kiro")
            data = source.read_bytes()
            if source.suffix == ".txt" or source.name == "SKILL.md":
                data = data.decode("utf-8").replace("__HUMANIZE_ROOT__", runtime.as_posix()).encode("utf-8")
            replacements[runtime / relative] = data
    for role in ROLES:
        config = json.loads((SOURCE / ".kiro/agents" / f"{role}.json").read_text(encoding="utf-8"))
        config["prompt"] = f"file://{runtime.as_posix()}/prompts/{role}.txt"
        if role == "humanize-korean":
            config["resources"] = [f"file://{runtime.as_posix()}/skills/humanize-korean/SKILL.md"]
        replacements[kiro_home / "agents" / f"{role}.json"] = (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    replacements[runtime / "LICENSE"] = (SOURCE / "LICENSE").read_bytes()
    if (SOURCE / "UPSTREAM.json").is_file():
        replacements[runtime / "UPSTREAM.json"] = (SOURCE / "UPSTREAM.json").read_bytes()
    retired = [kiro_home / "agents" / f"{name}.json" for name in LEGACY]
    retired += [kiro_home / "prompts" / f"{name}.txt" for name in (*LEGACY, "humanize-korean", "humanize-monolith")]
    retired += [kiro_home / "skills/humanize-korean" / name for name in ("SKILL.md", "references/quick-rules.md")]
    return replacements, retired


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".humanize-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kiro-home", type=Path, default=Path.home() / ".kiro", help="Kiro configuration directory (default: ~/.kiro)")
    parser.add_argument("--dry-run", action="store_true", help="Show planned changes without writing files")
    args = parser.parse_args(argv)
    kiro_home = args.kiro_home.expanduser().resolve()
    if kiro_home == (SOURCE / ".kiro").resolve():
        raise ValueError("The checkout already works as a project agent; choose a separate --kiro-home for installation")
    replacements, retired = install_plan(kiro_home)
    for target in [*replacements, *retired, kiro_home / "backups" / PACKAGE]:
        for part in (target, *target.parents):
            if part == kiro_home:
                break
            if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
                raise ValueError(f"Refusing redirected install path: {part}")
    changed = {path: data for path, data in replacements.items() if not path.is_file() or path.read_bytes() != data}
    existing_retired = [path for path in retired if path.is_file()]
    if args.dry_run:
        for path in changed:
            print(f"WRITE {path}")
        for path in existing_retired:
            print(f"BACKUP + RETIRE {path}")
        return 0
    old = {path: path.read_bytes() for path in [*changed, *existing_retired] if path.is_file()}
    backup = kiro_home / "backups" / PACKAGE / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    for path, data in old.items():
        atomic_write(backup / path.relative_to(kiro_home), data)
    for path, data in changed.items():
        atomic_write(path, data)
    for path in existing_retired:
        path.unlink()
    print(f"Installed {PACKAGE}: {len(changed)} changed files, {len(existing_retired)} retired files")
    if old:
        print(f"Previous files: {backup}")
    print("Run: kiro-cli chat --agent humanize-korean")
    return 0


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10+ is required")
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"Installation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
