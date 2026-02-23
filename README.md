# Parallel Workspace v5

요청 반영 버전입니다.

## 변경 사항
- 입력 / 실행 / 결론 중심으로 화면 단순화
- 부가 UI 대폭 축소(카테고리/프로젝트/저장만 미니바 유지)
- 결론 모드 추가: 기본, 비판, 추론, 합의, 비판+추론+합의
- 6개 모델 대형 출력창 유지
- 저장/복원(localStorage) 유지
- **404 방지용 `index.html` 추가** (루트 접속 시 자동으로 `parallel_ai_studio.html` 이동)

## 실행 (중요)
반드시 **`parallel_ai_studio.html` 파일이 있는 폴더**에서 실행하세요.

```bash
python -m http.server 4173
```

브라우저 접속:
- `http://localhost:4173/` (권장, index 자동 이동)
- `http://localhost:4173/parallel_ai_studio.html`

## 404가 뜰 때 체크
- 현재 터미널 위치가 저장소 루트인지 확인: `pwd` 또는 `Get-Location`
- 해당 위치에 파일이 있는지 확인: `ls` 또는 `dir`
- 경로에 오타가 없는지 확인 (`parallel_ai_studio.html`)
