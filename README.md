# 부동산 공공고시 통합 대시보드 (로컬)

로컬 환경에서 **정부/지자체 부동산 관련 고시·공고·회의록·입찰·공간정보**를 수집하고,
"공개자료 → 현장검증" 루틴으로 검증 계층을 쌓는 대시보드입니다.

## 대시보드 설계 개념
- **수집 레이어**: 기관별 공개 API/공고 페이지를 소스 단위로 관리 (`config/sources.json` 권장).
- **정규화 레이어**: 서로 다른 원천 문서를 `documents` 스키마로 통합 저장.
- **검증 레이어**: 수요·정책·교통·이해관계자 4축으로 점수화(`validations`).
- **운영 레이어**: 로컬 브라우저 UI에서 동기화/검색/검증 루프를 반복.

## 설치 방법 (Windows 기준, Git 포함)
### 0) Git 설치 확인
```powershell
git --version
```
- 버전이 나오면 설치됨
- 안 나오면: https://git-scm.com/download/win 에서 설치 후 PowerShell 재실행

### 1) 프로젝트 받기
```powershell
cd C:\Users\GSN\TC
git clone <저장소주소> gpt
cd C:\Users\GSN\TC\gpt
```

> 이미 폴더가 있다면 `git clone`은 생략하고 `cd C:\Users\GSN\TC\gpt`만 실행하세요.

### 2) Python 설치 확인
```powershell
python --version
```
- 버전이 나오면 OK
- 안 나오면 Microsoft Store 또는 https://www.python.org/downloads/ 에서 설치

### 3) 로컬 대시보드 실행 (패키지 설치 없이 가능)
```powershell
cd C:\Users\GSN\TC\gpt
dir run_local.py
python .\run_local.py
```

### 4) 브라우저 접속
- `http://127.0.0.1:8000`

### 5) 종료
- 실행 중인 창에서 `Ctrl + C`

## 실행하는 법 (가장 빠른 방법)
### 1) 서버 실행
```bash
python run_local.py
```

### 2) 브라우저 접속
- `http://127.0.0.1:8000`

### 3) 화면에서 바로 실행
1. `전체 소스 동기화` 클릭
2. 키워드/지역 입력 후 `문서 검색`
3. 문서 행의 `검증` 버튼 클릭

### 4) 종료
- 터미널에서 `Ctrl + C`


## Windows에서 안 될 때 (그림 상황 해결)
에러 원인: `run_local.py` 파일이 있는 폴더가 아닌 곳(`C:\Users\GSN\TC`)에서 실행해서입니다.

### PowerShell에서 그대로 따라하기
```powershell
# 1) 프로젝트 폴더로 이동 (run_local.py가 있는 위치)
cd C:\Users\GSN\TC\gpt

# 2) 파일 있는지 확인
dir run_local.py

# 3) 실행
python .\run_local.py
```

### Git Bash를 쓰고 싶다면
PowerShell에서 `bash` 명령이 없는 PC도 많습니다. 그 경우 그냥 **PowerShell만 사용**하세요.
(Git Bash 설치가 되어 있으면 Git Bash를 직접 열어서 아래처럼 실행)
```bash
cd /c/Users/GSN/TC/gpt
python run_local.py
```

### 100% 체크 포인트
- `dir run_local.py` 결과에 파일이 보여야 함
- 그 다음에 `python .\run_local.py` 실행
- 브라우저: `http://127.0.0.1:8000`

## 터미널로 동작 확인 (선택)
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/overview
curl -X POST http://127.0.0.1:8000/sync
curl "http://127.0.0.1:8000/documents?keyword=도시관리계획&region=서울&limit=100"
curl -X POST http://127.0.0.1:8000/validate/1
```

## 실제 데이터 연결
- 기본값은 테스트용 fallback 문서를 넣습니다.
- 실제 수집을 하려면 `config/sources.json`에서 소스별 `endpoint`, `params`, `api_key` 값을 채우면 됩니다.

## 포함 범위
- 나라장터(입찰공고/과업지시서)
- 대도시권광역교통위원회 회의록
- 서울시 도시계획 포털
- 경기도 부동산 포털
- 택지정보시스템
- 지자체 공고/열람공고/결정고시/승인
- 국가공간정보, 공공데이터포털(OpenAPI), 온비드, 상권정보시스템, V월드
- 전략/환경영향평가(소규모 포함), 통계청, 한국부동산원

## 핵심 워크플로우
1. `/sync`로 전체 소스 동기화
2. `/documents`로 키워드/지역 후보 탐색
3. `/validate/{id}`로 검증 점수 계산
4. `/overview` 카드로 운영 현황 확인
5. 노션 SOP 템플릿으로 현장검증 체크리스트 실행
