from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class Pillar(str, Enum):
    BUILDER = "제작자(Builder)"
    HUNTER = "사냥꾼(Hunter)"
    STORYTELLER = "스토리텔러(Storyteller)"
    NAVIGATOR = "항해사(Navigator)"
    OPERATOR = "운영자(Operator)"
    STRATEGIST = "전략가(Strategist)"


@dataclass
class Task:
    pillar: Pillar
    objective: str
    tools: List[str]
    output: str


@dataclass
class WeeklySystem:
    business_goal: str
    bottleneck: Pillar
    hours_budget: int = 5
    tasks: List[Task] = field(default_factory=list)

    def auto_design(self) -> None:
        """트랜스크립트의 6각 구조를 5시간 운영 플랜으로 자동 배치한다."""
        task_map: Dict[Pillar, Task] = {
            Pillar.BUILDER: Task(
                pillar=Pillar.BUILDER,
                objective="자연어로 MVP를 제작하고 배포한다.",
                tools=["Lovable", "Bolt", "Cursor"],
                output="MVP URL + 핵심 기능 3개 동작 확인",
            ),
            Pillar.HUNTER: Task(
                pillar=Pillar.HUNTER,
                objective="리드 발굴/개인화 아웃리치를 자동화한다.",
                tools=["Outbound", "Fireflies", "Clay"],
                output="고품질 리드 30개 + 맞춤 메시지 30개",
            ),
            Pillar.STORYTELLER: Task(
                pillar=Pillar.STORYTELLER,
                objective="1개의 원본 콘텐츠를 멀티채널로 변환한다.",
                tools=["Claude Project", "Runway", "Canva"],
                output="블로그 1개 + 쇼츠 1개 + 썸네일 2개",
            ),
            Pillar.NAVIGATOR: Task(
                pillar=Pillar.NAVIGATOR,
                objective="SEO에서 AEO로 전환하고 답변 노출을 최적화한다.",
                tools=["Profound", "Athena", "Google Search Console"],
                output="핵심 질문 10개에 대한 인용형 문서 업데이트",
            ),
            Pillar.OPERATOR: Task(
                pillar=Pillar.OPERATOR,
                objective="이메일/일정/CRM 업데이트를 에이전트에 위임한다.",
                tools=["Zapier", "HubSpot", "Calendar API"],
                output="반복 업무 3개 자동화 + SLA 24시간 이내",
            ),
            Pillar.STRATEGIST: Task(
                pillar=Pillar.STRATEGIST,
                objective="비즈니스 컨텍스트를 주입한 AI 자문 보드를 구축한다.",
                tools=["Claude Project", "Notion", "Spreadsheet"],
                output="주간 의사결정 메모 1개 + 리스크/실험 우선순위",
            ),
        }

        # 병목 영역은 2시간, 나머지 5개 영역은 30분씩 배정 (총 4.5시간)
        # 남은 30분은 전략 리뷰로 고정한다.
        self.tasks.clear()
        ordered = [
            self.bottleneck,
            Pillar.BUILDER,
            Pillar.HUNTER,
            Pillar.STORYTELLER,
            Pillar.NAVIGATOR,
            Pillar.OPERATOR,
            Pillar.STRATEGIST,
        ]
        seen = set()
        unique_order = [p for p in ordered if not (p in seen or seen.add(p))]
        for pillar in unique_order:
            self.tasks.append(task_map[pillar])

    def weekly_plan(self) -> List[str]:
        if not self.tasks:
            self.auto_design()

        plan: List[str] = []
        total_minutes = self.hours_budget * 60
        used = 0

        for idx, task in enumerate(self.tasks):
            minutes = 120 if task.pillar == self.bottleneck else 30
            if used + minutes > total_minutes:
                continue
            used += minutes
            plan.append(
                f"{idx+1}. [{minutes:>3}분] {task.pillar.value}: {task.objective} | 툴={', '.join(task.tools)} | 산출물={task.output}"
            )

        if used < total_minutes:
            plan.append(
                f"{len(plan)+1}. [{total_minutes-used:>3}분] 전략 리뷰: 지표 회고, 다음 주 병목 재선정"
            )

        return plan


if __name__ == "__main__":
    system = WeeklySystem(
        business_goal="2027년까지 1인 AI 비즈니스 월 5천만원 매출",
        bottleneck=Pillar.STORYTELLER,
    )
    print("\n=== 6대 AI 핵심기술 기반 주간 운영 계획 ===")
    print(f"목표: {system.business_goal}")
    print(f"주간 운영 시간: {system.hours_budget}시간\n")

    for line in system.weekly_plan():
        print(line)
