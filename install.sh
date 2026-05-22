#!/bin/bash
set -e

KIRO_DIR="$HOME/.kiro"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "im-not-ai-kiro 설치 중..."

# 디렉토리 생성
mkdir -p "$KIRO_DIR/agents" "$KIRO_DIR/prompts" "$KIRO_DIR/skills/humanize-korean/references"

# 복사
cp "$SCRIPT_DIR/.kiro/agents/"*.json "$KIRO_DIR/agents/"
cp "$SCRIPT_DIR/.kiro/prompts/"*.txt "$KIRO_DIR/prompts/"
cp "$SCRIPT_DIR/.kiro/skills/humanize-korean/SKILL.md" "$KIRO_DIR/skills/humanize-korean/"
cp "$SCRIPT_DIR/.kiro/skills/humanize-korean/references/quick-rules.md" "$KIRO_DIR/skills/humanize-korean/references/"

# 플레이스홀더를 실제 경로로 치환
for f in "$KIRO_DIR/agents/"humanize-*.json "$KIRO_DIR/agents/"ai-tell-*.json "$KIRO_DIR/agents/"korean-*.json "$KIRO_DIR/agents/"content-*.json "$KIRO_DIR/agents/"naturalness-*.json; do
  [ -f "$f" ] && sed -i "s|__KIRO_HOME__|$KIRO_DIR|g" "$f"
done

echo "✓ 설치 완료!"
echo ""
echo "사용법:"
echo "  kiro-cli chat 실행 후 /agent swap humanize-korean"
echo "  또는 Ctrl+Shift+H 단축키"
