# 원본 동기화 기록

- 원본: [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai)
- 반영 기준: [`9747f036cdc28a1a8aea4dc71fef1f7846eb96f7`](https://github.com/epoko77-ai/im-not-ai/commit/9747f036cdc28a1a8aea4dc71fef1f7846eb96f7) (2026-09-06)
- 확인일: 2026-09-14
- 원본 스킬 메타데이터 버전: 2.3.2. 이후 규칙 변경도 포함하므로 커밋 해시가 정확한 기준이다.

## 반영 범위

1. 분류 체계와 생성된 quick-rules·diagnosis-rules, 윤문 처방, 학술 근거, 장르별 baseline 및 metrics.
   현재 진단 인덱스 84개 항목, quick-rules 대상 61개 항목을 포함한다. 보류 항목도 있어 이를 탐지 정확도나 활성 패턴 수로 해석하지 않는다.
2. 입력 정규화·사전 점수·route_hint, 긴 글 청킹·재조립, 서법 복원, 주입된 쉼표 제거, 구조·의미 보존 게이트.
3. light/standard/heavy 경로와 diagnostician → monolith → finalizer 역할.
4. 런타임·생성 규칙·골든 fixture의 오프라인 회귀 테스트.

`UPSTREAM.json`의 `files`는 **바이트 단위로 원본과 동일한 파일**이다. 경로만 `.kiro/` 아래로 옮겼고 Git blob SHA로 검증한다. 원본 `scripts/`와 `skills/`의 상대 배치를 보존해 경로 탐색 코드를 수정하지 않았다. 테스트도 같은 이유로 `.kiro/tests/`에 있다. 설치 시 테스트 파일은 배포하지 않는다.

`adapted_files`는 Kiro에 맞게 수정한 워크플로·역할 프롬프트다. 주요 차이는 다음과 같다.

- Claude 전용 도구·모델·플러그인 변수 대신 Kiro 도구와 설치 시 확정되는 절대 경로를 사용한다.
- 실행 역할 3개만 위임 가능하게 제한하며 모델은 사용자의 Kiro 설정을 따른다.
- monolith에 `output_path`와 `output_format`을 명시해 청크들이 같은 final.md를 덮어쓰지 않게 한다.
- body 청크가 하나여도 manifest가 있으면 재조립해 passthrough 각주를 보존한다.
- shim 오류 파일이 있으면 이전 metrics를 무시한다. 재윤문은 새 run 폴더에서 시작한다.
- finalize 뒤에도 서법 복원·쉼표 정리·게이트를 다시 실행하며 실패를 성공으로 보고하지 않는다.

Claude/Codex/Gemini/Copilot 배포 매니페스트, 원본 플랫폼 설치기, 개발·연구용 에이전트, 라이브 Claude 평가기와 이미지 생성 스크립트는 이 포트의 실행 범위에 포함하지 않는다. 그 플랫폼에 종속된 테스트는 Kiro 설치·경로·역할 검증으로 대체했다. 원본 참고 문서의 역사적 버전·플랫폼 설명은 출처 보존을 위해 그대로 두며, Kiro 실행 절차는 이 저장소의 README와 SKILL.md를 따른다.

## 다음 동기화 절차

1. 원본 main의 새 커밋을 확인하고 이 문서와 `UPSTREAM.json`의 커밋을 갱신한다.
2. `files`의 원본 경로에서 파일을 그대로 가져오고 blob SHA를 갱신한다. `adapted_files`는 차이를 비교해 Kiro 호출 계약을 유지하며 반영한다.
3. taxonomy를 수정했다면 아래 명령으로 파생 파일을 생성한다.

   ```sh
   python3 .kiro/scripts/build_quick_rules.py
   python3 .kiro/scripts/build_diagnosis_rules.py
   ```

4. `python3 -m unittest discover -s .kiro/tests -q`와 두 생성기의 `--check`를 실행한다. 의도적으로 원본 파일을 수정했다면 `files`의 무변경 목록에서 빼고 이유를 기록한다.
5. `bash install.sh --dry-run`으로 설치 계획을 확인하고 임시 설치에서 Kiro 에이전트 선택·위임을 직접 검증한다.
6. 규칙·런타임, Kiro 포트, 설치·문서 변경을 각각 커밋한다.

라이선스와 원본 저작권 표기는 [LICENSE](LICENSE)를 따른다.
