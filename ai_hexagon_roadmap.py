from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Sequence


class Pillar(str, Enum):
    BUILDER = "제작자(Builder)"
    HUNTER = "사냥꾼(Hunter)"
    STORYTELLER = "스토리텔러(Storyteller)"
    NAVIGATOR = "항해사(Navigator)"
    OPERATOR = "운영자(Operator)"
    STRATEGIST = "전략가(Strategist)"


@dataclass(frozen=True)
class TaskTemplate:
    objective: str
    tools: Sequence[str]
    output: str
    one_person_strategy: str


@dataclass
class PlanItem:
    pillar: Pillar
    minutes: int
    objective: str
    tools: Sequence[str]
    output: str
    one_person_strategy: str


@dataclass
class WeeklySystem:
    business_goal: str
    bottleneck: Pillar
    hours_budget: int = 5
    task_templates: Dict[Pillar, TaskTemplate] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.hours_budget <= 0:
            raise ValueError("hours_budget는 1 이상이어야 합니다.")
        if not self.task_templates:
            self.task_templates = default_task_templates()

    def _ordered_pillars(self) -> List[Pillar]:
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
        return [p for p in ordered if not (p in seen or seen.add(p))]

    def weekly_plan(self) -> List[PlanItem]:
        total_minutes = self.hours_budget * 60
        used = 0
        plan: List[PlanItem] = []

        for pillar in self._ordered_pillars():
            minutes = 120 if pillar == self.bottleneck else 30
            if used + minutes > total_minutes:
                continue
            template = self.task_templates[pillar]
            plan.append(
                PlanItem(
                    pillar=pillar,
                    minutes=minutes,
                    objective=template.objective,
                    tools=template.tools,
                    output=template.output,
                    one_person_strategy=template.one_person_strategy,
                )
            )
            used += minutes

        remaining = total_minutes - used
        if remaining > 0:
            plan.append(
                PlanItem(
                    pillar=Pillar.STRATEGIST,
                    minutes=remaining,
                    objective="지표 회고 + 다음 주 병목 재선정",
                    tools=["Notion", "Spreadsheet"],
                    output="다음 주 실험 우선순위 3개",
                    one_person_strategy="실행은 AI에게, 의사결정은 인간이 맡는 지휘 구조를 유지",
                )
            )
        return plan


def default_task_templates() -> Dict[Pillar, TaskTemplate]:
    return {
        Pillar.BUILDER: TaskTemplate(
            objective="자연어 프롬프트로 MVP를 제작하고 고객 검증 가능한 형태로 배포",
            tools=["Lovable", "Bolt", "Cursor"],
            output="MVP URL + 핵심 유저 플로우 1개 동작 영상",
            one_person_strategy="개발팀 없이도 아이디어→출시 사이클을 며칠 단위로 압축",
        ),
        Pillar.HUNTER: TaskTemplate(
            objective="리드 발굴-데이터 강화-개인화 아웃리치 자동화",
            tools=["Clay", "Fireflies", "Apollo"],
            output="타깃 리드 30개 + 개인화 메시지 30개",
            one_person_strategy="탐색/반복은 AI가 담당, 인간은 클로징/신뢰 형성에 집중",
        ),
        Pillar.STORYTELLER: TaskTemplate(
            objective="원본 아이디어 1개를 멀티채널 콘텐츠로 재가공",
            tools=["Claude Project", "Runway", "Canva"],
            output="블로그 1개 + 숏폼 1개 + 썸네일 2개",
            one_person_strategy="'나의 톤' 데이터를 학습시켜 24시간 콘텐츠 파이프라인 구축",
        ),
        Pillar.NAVIGATOR: TaskTemplate(
            objective="SEO 중심 사고에서 AEO(Answer Engine Optimization) 체계로 전환",
            tools=["Profound", "Athena", "Search Console"],
            output="핵심 질문 10개 대응 문서 + 인용 가능 근거 업데이트",
            one_person_strategy="웹사이트 클릭 경쟁보다 AI 답변 내 인용/추천 점유율을 우선 관리",
        ),
        Pillar.OPERATOR: TaskTemplate(
            objective="이메일/일정/CRM 업데이트 등 백오피스 반복 작업 자동화",
            tools=["Zapier", "HubSpot", "Calendar API"],
            output="반복업무 3개 자동화 + 응답 SLA 24시간 이내",
            one_person_strategy="에이전트에게 실행 권한을 위임해 운영 병목 제거",
        ),
        Pillar.STRATEGIST: TaskTemplate(
            objective="비즈니스 컨텍스트를 주입한 AI 이사회(자문 보드) 운영",
            tools=["Claude Project", "Notion", "Spreadsheet"],
            output="주간 전략 메모 1개 + 리스크/실험 우선순위",
            one_person_strategy="리더의 고독을 줄이고 데이터 기반 전략 의사결정 품질 향상",
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="2027 AI 육각형 로드맵을 1인 기업 실행계획으로 생성합니다."
    )
    parser.add_argument("--goal", default="2027년까지 1인 AI 비즈니스 월 5천만원 매출")
    parser.add_argument(
        "--bottleneck",
        default="storyteller",
        choices=[p.name.lower() for p in Pillar],
        help="현재 가장 막힌 영역",
    )
    parser.add_argument("--hours", type=int, default=5, help="주간 집중 운영 시간")
    return parser.parse_args()


def pillar_from_text(value: str) -> Pillar:
    return Pillar[value.upper()]


def print_plan(system: WeeklySystem) -> None:
    print("\n=== 2027 AI 육각형 1인기업 실행계획 ===")
    print(f"목표: {system.business_goal}")
    print(f"병목: {system.bottleneck.value}")
    print(f"주간 운영 시간: {system.hours_budget}시간")
    print("핵심 원칙: 하루 30분씩 병목을 자동화하고, 인간은 전략/질문/결정에 집중\n")

    for idx, item in enumerate(system.weekly_plan(), start=1):
        print(f"{idx}. [{item.minutes:>3}분] {item.pillar.value}")
        print(f"   - 목표: {item.objective}")
        print(f"   - 툴: {', '.join(item.tools)}")
        print(f"   - 산출물: {item.output}")
        print(f"   - 1인기업 전략: {item.one_person_strategy}\n")


if __name__ == "__main__":
    args = parse_args()
    system = WeeklySystem(
        business_goal=args.goal,
        bottleneck=pillar_from_text(args.bottleneck),
        hours_budget=args.hours,
    )
    print_plan(system)
