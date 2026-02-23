# Parallel Workspace v5

요청 반영 버전입니다.

## 변경 사항
- 입력 / 실행 / 결론 중심으로 화면 단순화
- 부가 UI 대폭 축소(카테고리/프로젝트/저장만 미니바 유지)
- 결론 모드 추가: 기본, 비판, 추론, 합의, 비판+추론+합의
- 6개 모델 대형 출력창 유지
- 저장/복원(localStorage) 유지
- 실행 진입점 추가: `index.html`, `parallel-ai-studio.html` (리다이렉트)

## 실행
```bash
# 1) 저장소 루트(GPT)에서 실행
python -m http.server 4173

# 2) 브라우저 접속
# 기본 진입: http://localhost:4173/
# 직접 진입: http://localhost:4173/parallel_ai_studio.html
```

## 404(File not found) 해결
- `python -m http.server`를 **반드시 `GPT` 폴더에서 실행**하세요.
- 아래 파일이 있는지 확인하세요.
  - `parallel_ai_studio.html`
  - `index.html`
- 경로 오타가 없는지 확인하세요. (`parallel_ai_studio.html` 언더스코어 `_`)
