# im-not-ai-kiro

AI가 쓴 한글 글의 번역투·상투구·기계적인 문장 구조를 다듬는 [Kiro CLI](https://kiro.dev/) 에이전트입니다. 사실·수치·인용·핵심 개념과 원문의 격식은 보존합니다.

[epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai)의 커뮤니티 포트입니다. 
2026-09-06 원본 커밋 [`9747f036cdc2`](https://github.com/epoko77-ai/im-not-ai/commit/9747f036cdc28a1a8aea4dc71fef1f7846eb96f7)까지 반영했습니다.

정확한 파일 목록과 Kiro 변환 사항은 [UPSTREAM.md](UPSTREAM.md), 원본 파일 해시는 [UPSTREAM.json](UPSTREAM.json)에 있습니다.

## 설치 및 업데이트

Kiro CLI 3.0+와 Python 3.10+가 필요합니다. Python 추가 패키지는 필요하지 않습니다.

macOS/Linux:

```sh
git clone https://github.com/Gaeduck-0908/im-not-ai-kiro.git
cd im-not-ai-kiro
bash install.sh
```

Windows(Python 3가 `python`으로 실행되는 환경):

```powershell
git clone https://github.com/Gaeduck-0908/im-not-ai-kiro.git
cd im-not-ai-kiro
python install.py
```

기존 설치 업데이트:

```sh
git pull --ff-only
bash install.sh
```

Windows에서는 마지막 줄을 `python install.py`로 바꿉니다. Kiro 실행 중이었다면 세션을 다시 시작하세요.

- 에이전트 4개는 `~/.kiro/agents/`, 프롬프트·규칙·Python 스크립트는 `~/.kiro/im-not-ai-kiro/`에 설치합니다.
- 설치 시 프롬프트와 리소스 경로를 절대 경로로 바꿔 다른 프로젝트 폴더에서도 사용할 수 있습니다.
- 교체하거나 폐기하는 이 포트의 기존 파일은 `~/.kiro/backups/im-not-ai-kiro/<시각>/`에 먼저 백업합니다. 구형 4개 역할과 이전 프롬프트·스킬 파일도 백업 후 정리합니다. 다른 이름의 에이전트와 사용자 추가 파일은 유지합니다.
- 이미 최신 상태인 파일은 다시 쓰지 않습니다. `--dry-run`은 파일을 변경하지 않습니다.

```sh
bash install.sh --dry-run
bash install.sh --kiro-home /path/to/kiro
```

저장소에서 직접 실행할 때는 프로젝트 `.kiro/` 구성을 사용할 수 있습니다. 설치 템플릿을 수동 복사하는 대신 설치기를 사용하세요.

## 사용법

```sh
kiro-cli chat --agent humanize-korean
```

기존 채팅에서는 `/agent swap humanize-korean`으로 전환합니다.

```text
AI 티 없애줘:
[윤문할 텍스트]
```

파일 경로를 주거나 아래 옵션을 자연어로 덧붙일 수 있습니다.

- `장르: 칼럼|리포트|블로그|공적|학술`
- `강도: 보수|기본|적극`
- `--strict` 또는 `정밀 모드`: heavy 경로 강제
- `가볍게` 또는 `빠르게만`: light 경로 강제
- `이 문단만`, `특정 카테고리만 다시`, `2차 윤문`: 범위를 정해 새 실행으로 처리

결과는 **사용자 작업 폴더**의 `_workspace/<날짜-번호>/final.md`에 저장합니다. 메트릭·진단·검증 결과도 같은 실행 폴더에 남깁니다. shell 도구의 승인 설정은 사용자의 Kiro 설정을 따릅니다.

## 처리 경로

| 경로 | 기본 흐름 | 용도 |
|---|---|---|
| light | 윤문 1회 + 코드 검증 | 손댈 곳이 적은 글, 보수적 수정 |
| standard | 진단 → 윤문 + 코드 검증 | 보통의 AI 초안 |
| heavy | 진단 → 윤문 → 마무리 검사 + 코드 검증 | 정밀 요청, 의미 보존 검증이 필요한 글 |

입력 분석 스크립트의 `route_hint`로 자동 선택하며 사용자 지정이 우선합니다. 긴 글도 단일 호출을 우선하고, heavy에서 실제 분할된 경우에만 청크별로 처리합니다. 각주처럼 그대로 보존할 부분은 재조립 시 원문에서 복원합니다.

원본의 최신 분류 체계, 장르별 정량 점수, 유니코드 정규화, 서법 복원과 쉼표 주입 방지 기능을 포함합니다. 변경률뿐 아니라 수치·인용·각주·제목·격식과 서법 손실도 검사합니다. 점수는 윤문 경로 선택을 위한 참고값이며 저자 판별 확률이 아닙니다.

검증 결과가 경고면 해당 항목을 알리고 마무리 검사를 수행합니다. **변경률 30% 이상은 경고, 50% 이상은 채택 중단**입니다. 재시도해도 해결되지 않거나 검증 코드를 실행할 수 없으면 성공으로 보고하지 않습니다.

## 구성과 검증

```text
.kiro/
├── agents/                 # 오케스트레이터 + 실행 역할 3개
├── prompts/                # Kiro용 역할 프롬프트
├── scripts/                # 원본 Python 런타임·규칙 생성기
├── skills/humanize-korean/  # Kiro 워크플로와 원본 references
└── tests/                  # 오프라인 회귀·Kiro 설치 검증 (설치 대상 아님)
install.py                  # 공통 설치기
install.sh                  # macOS/Linux 진입점
UPSTREAM.json               # 원본 커밋과 파일 해시
```

저장소 루트에서 실행합니다.

```sh
python3 -m unittest discover -s .kiro/tests -q
python3 .kiro/scripts/build_quick_rules.py --check
python3 .kiro/scripts/build_diagnosis_rules.py --check
```

Windows는 `python3` 대신 `python`을 사용합니다. CI는 Linux·macOS·Windows의 Python 3.10/3.12에서 같은 검사를 수행합니다. 오프라인 테스트는 실제 LLM 응답 품질이나 Kiro 인증·위임 실행을 검증하지 않습니다. 실제 실행 점검은 [SMOKE_TEST.md](SMOKE_TEST.md)를 따릅니다.

## 크레딧·라이선스

분류 체계·윤문 처방·검증 코드·에이전트 설계는 [원본 im-not-ai](https://github.com/epoko77-ai/im-not-ai)에서 유래합니다. 이 저장소는 Kiro용 실행·설치 구성을 제공합니다. MIT — [LICENSE](LICENSE).
