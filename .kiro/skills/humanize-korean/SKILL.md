---
name: humanize-korean
description: AI(ChatGPT·Claude·Gemini 등)가 쓴 한글 텍스트를 내용은 건드리지 않고 문체·리듬·표현만 자연스러운 한국어로 윤문하는 스킬. "AI 티 없애줘", "번역투 제거", "사람이 쓴 것처럼 윤문" 등의 요청에 자동 발동.
---

# Humanize Korean — AI 한글 티 제거 오케스트레이터 (v2.0)

AI가 쓴 한글 글의 번역투·영어 인용 과다·기계적 병렬·관용구·피동태 남용·접속사 남발·리듬 균일성 등 10대 카테고리 × 40+ 패턴을 탐지해 내용은 보존하고 문체만 자연스럽게 되돌린다.

## 트리거 키워드

"AI 티 없애줘", "GPT 문체 제거", "사람이 쓴 것처럼 윤문", "번역투 제거", "AI 윤문", "humanize Korean", "AI 글 자연스럽게"

## 모드 결정

- **Fast (디폴트)**: 5,000자 이하. `humanize-monolith` 에이전트 1회 호출.
- **Strict**: `--strict` 명시 또는 8,000자+ 자동 승급. 5인 파이프라인(detector → rewriter → auditor + reviewer → 종합).

## 4대 철칙

1. **의미 불변** — 사실·주장·수치·고유명사·직접 인용 100% 보존.
2. **근거 기반** — 탐지된 span에만 수술적 수정.
3. **장르 유지** — 칼럼→문학, 리포트→에세이 이탈 금지.
4. **과윤문 금지** — 변경률 30% 초과 경고, 50% 초과 강제 중단.

## Fast 모드 워크플로

1. `_workspace/{run_id}/01_input.txt`에 입력 저장
2. `humanize-monolith` 에이전트 호출 (탐지·윤문·자체검증 일괄)
3. `_workspace/{run_id}/final.md` 산출

## Strict 모드 워크플로

1. `ai-tell-detector` → `02_detection.json`
2. `korean-style-rewriter` → `03_rewrite.md`
3. 병렬 검증: `content-fidelity-auditor` + `naturalness-reviewer`
4. 종합 판정 → accept / rewrite_round_2 / rollback / hold_and_report

## 참조 파일

- [`references/quick-rules.md`](references/quick-rules.md) — S1·S2 핵심 패턴 슬림 룰북
