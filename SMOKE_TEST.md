# Kiro 실행 점검

오프라인 테스트와 별도로, Kiro CLI 3.0+가 설치·인증된 환경에서 확인합니다.
아래는 수동 실행 절차이며 테스트를 실행했다는 기록이 아닙니다.

1. `bash install.sh`(Windows: `python install.py`)로 설치하고 저장소와 다른 작업 폴더에서 `kiro-cli chat --agent humanize-korean`을 시작합니다.
2. `가볍게 윤문해줘: 정부는 예산을 늘려야 한다. 참여자는 1,200명이다.`를 요청합니다. monolith 1회, Python 게이트 실행, cwd 아래 `final.md` 생성을 확인합니다. 원문의 요구 표현과 수치가 유지되어야 합니다.
3. 같은 글에 `--strict`를 붙여 요청합니다. diagnostician → monolith → finalizer의 순서, `02_diagnosis.md`와 `09_finalize.json`, finalize 후 게이트 재실행을 확인합니다.
4. 학술 글에 제목·인용·각주를 포함해 요청합니다. 원문과 결과의 제목·인용·각주가 보존되어야 합니다. 청크 처리 시 각 body의 결과 파일 이름이 달라야 하고, `03_reassembly_report.json`에 경고가 없어야 합니다.
5. `2차 윤문`을 요청합니다. 이전 실행 파일은 남고 새 실행 폴더가 생성되어야 합니다.
6. 경로·역할 로드·Python 실행이 실패하면 성공으로 보고하지 않고 실제 오류를 알려야 합니다.

결과에 실행한 Kiro 버전, 선택 모델, 운영체제, 실행 경로(light/standard/heavy), 게이트 상태를 함께 기록합니다. 문체 품질은 원문과 결과를 직접 읽고 판단합니다.
