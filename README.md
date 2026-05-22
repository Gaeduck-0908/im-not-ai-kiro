# im-not-ai-kiro

> AI가 쓴 한글 글의 "AI 티"를 제거하는 [Kiro CLI](https://kiro.dev) 에이전트 포트.

[epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai) (Claude Code 스킬)를 Kiro CLI agent 형식으로 변환한 커뮤니티 포트입니다.

## 뭘 하는 건가요?

ChatGPT·Claude·Gemini 등이 쓴 한글 텍스트를 **내용은 건드리지 않고** 문체·리듬·표현만 자연스러운 한국어로 윤문합니다.

- 번역투("~를 통해", "~에 있어서") 제거
- AI 관용구("결론적으로", "시사하는 바가 크다") 삭제
- 기계적 병렬·이모지·불릿 남용 정리
- 10대 카테고리 × 40+ 패턴 탐지 후 수술적 수정

## 설치

```bash
git clone https://github.com/Gaeduck-0908/im-not-ai-kiro.git
cd im-not-ai-kiro
./install.sh
```

`install.sh`가 `~/.kiro/` 아래에 에이전트·프롬프트·스킬 파일을 복사합니다.

### 수동 설치

```bash
cp -r .kiro/agents/* ~/.kiro/agents/
cp -r .kiro/prompts/* ~/.kiro/prompts/
cp -r .kiro/skills/* ~/.kiro/skills/
```

## 사용법

### 1. 에이전트 전환

```
/agent swap humanize-korean
```

또는 단축키 `Ctrl+Shift+H`

### 2. 텍스트 윤문 요청

```
AI 티 없애줘:

[여기에 AI가 쓴 텍스트 붙여넣기]
```

다음 표현 중 아무거나 쓰면 됩니다:
- "AI 티 없애줘"
- "번역투 제거해줘"
- "사람이 쓴 것처럼 윤문해줘"
- "GPT 문체 제거"

### 3. 결과 확인

`_workspace/{날짜-번호}/final.md`에 윤문본이 저장됩니다.

## 모드

| 모드 | 조건 | 설명 |
|------|------|------|
| **Fast** (디폴트) | 5,000자 이하 | `humanize-monolith` 1회 호출. 2~3분. |
| **Strict** | `--strict` 또는 8,000자+ | 5인 파이프라인 (탐지→윤문→감사+리뷰→종합). |

## 에이전트 구성

```
.kiro/
├── agents/
│   ├── humanize-korean.json          # 메인 오케스트레이터
│   ├── humanize-monolith.json        # Fast 모드 단일 호출
│   ├── ai-tell-detector.json         # Strict: AI 티 탐지
│   ├── korean-style-rewriter.json    # Strict: 수술적 윤문
│   ├── content-fidelity-auditor.json # Strict: 의미 보존 감사
│   └── naturalness-reviewer.json     # Strict: 자연도 리뷰
├── prompts/
│   ├── humanize-korean.txt
│   ├── humanize-monolith.txt
│   ├── ai-tell-detector.txt
│   ├── korean-style-rewriter.txt
│   ├── content-fidelity-auditor.txt
│   └── naturalness-reviewer.txt
└── skills/humanize-korean/
    ├── SKILL.md
    └── references/
        └── quick-rules.md            # S1·S2 핵심 패턴 룰북
```

## 4대 철칙

1. **의미 불변** — 사실·수치·고유명사·인용 100% 보존
2. **근거 기반** — 탐지된 패턴에만 수정
3. **장르 유지** — 칼럼→문학 이탈 금지
4. **과윤문 금지** — 변경률 30% 초과 경고, 50% 초과 중단

## 요구사항

- [Kiro CLI](https://kiro.dev) 설치 필요

## 크레딧

- 원본: [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai) (MIT License)
- AI 티 분류 체계(taxonomy), 윤문 처방(playbook), 에이전트 아키텍처 설계 모두 원본 프로젝트에서 유래
- 본 레포는 Kiro CLI agent 형식으로의 변환(포트)입니다

## 라이선스

MIT — [LICENSE](LICENSE) 참조.

원본 프로젝트와 동일한 MIT 라이선스를 따릅니다.
