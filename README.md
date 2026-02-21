# AI Hexagon Roadmap (2027)

영상 트랜스크립트의 핵심 주장(6개 AI 축 + 주 5시간 지휘 모델)을 코드로 옮긴 예제입니다.

## 무엇을 하나요?
- 6개 축(제작/세일즈/콘텐츠/검색/운영/전략)을 데이터 구조로 모델링
- 병목 1개를 중심으로 주간 5시간 계획 자동 생성
- "하루 30분씩 레버리지" 메시지를 실행 가능한 스케줄로 변환

## 실행
```bash
python ai_hexagon_roadmap.py
```

## 커스터마이징
`ai_hexagon_roadmap.py`의 `WeeklySystem` 생성 시 아래를 바꾸세요.
- `business_goal`: 당신의 목표
- `bottleneck`: 현재 가장 막힌 영역 (`Pillar` enum)
- `hours_budget`: 주간 운영 시간 (기본 5시간)
