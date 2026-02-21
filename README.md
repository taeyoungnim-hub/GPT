# AI Hexagon Roadmap (2027)

유튜브 트랜스크립트의 핵심 주장(6개 AI 축 + 주 5시간 지휘 모델)을 **실행 가능한 코드**로 옮긴 예제입니다.

## 무엇을 하나요?
- 6개 축(제작/세일즈/콘텐츠/검색/AEO/운영/전략)을 데이터 모델로 정의
- 현재 병목 1개를 우선순위로 잡아 주간 시간(기본 5시간) 자동 배분
- "하루 30분씩 레버리지 축적" 메시지를 실제 계획표로 출력
- CLI 인자로 목표/병목/시간 예산 커스터마이징 가능

## 실행
```bash
python ai_hexagon_roadmap.py
```

## 옵션 예시
```bash
python ai_hexagon_roadmap.py --bottleneck operator --hours 6 \
  --goal "2027년까지 자동화 에이전시 월 1억원"
```

- `--bottleneck`: `builder | hunter | storyteller | navigator | operator | strategist`
- `--hours`: 주간 집중 운영 시간
- `--goal`: 비즈니스 목표 문장

## 출력 예시(요약)
- 병목 영역 120분
- 나머지 축 30분씩 순차 배정
- 남는 시간은 전략 리뷰(지표 회고 + 다음 주 병목 재선정)

