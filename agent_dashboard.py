#!/usr/bin/env python3
"""Reliable 6-agent orchestrator dashboard (CLI, stdlib only)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
from typing import Dict, List, Optional


class AgentStatus(str, Enum):
    IDLE = "대기"
    WORKING = "작업중"
    DONE = "완료"


class Priority(str, Enum):
    LOW = "낮음"
    MEDIUM = "보통"
    HIGH = "높음"


@dataclass
class Agent:
    key: str
    name: str
    domain: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: str = "-"
    recent_result: str = "아직 실행 기록 없음"


@dataclass
class Task:
    id: int
    title: str
    detail: str
    priority: Priority
    assigned_agent_key: str
    status: AgentStatus = AgentStatus.IDLE


@dataclass
class AssignmentLog:
    timestamp: str
    task_id: int
    agent_key: str
    input_text: str
    output_text: str
    is_error: bool = False


@dataclass
class Orchestrator:
    agents: Dict[str, Agent] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)
    logs: List[AssignmentLog] = field(default_factory=list)

    @staticmethod
    def default() -> "Orchestrator":
        agents = {
            "investment": Agent("investment", "투자 에이전트", "투자 분석"),
            "business": Agent("business", "사업 전략 에이전트", "사업 모델/전략"),
            "realestate": Agent("realestate", "부동산 에이전트", "입지/수익성 분석"),
            "tax": Agent("tax", "세무/회계 에이전트", "세금/재무 구조"),
            "legal": Agent("legal", "리스크/법무 에이전트", "법적 리스크 점검"),
            "operations": Agent("operations", "운영/일정 에이전트", "실행계획/일정관리"),
        }
        return Orchestrator(agents=agents)

    def add_project_goal(self, goal: str) -> None:
        clean_goal = goal.strip()
        if not clean_goal:
            raise ValueError("프로젝트 목표는 비어 있을 수 없습니다.")

        assignments = self._route_goal_to_agents(clean_goal)
        for agent_key, title, detail, priority in assignments:
            task = Task(
                id=len(self.tasks) + 1,
                title=title,
                detail=detail,
                priority=priority,
                assigned_agent_key=agent_key,
            )
            self.tasks.append(task)

    def _route_goal_to_agents(self, goal: str) -> List[tuple[str, str, str, Priority]]:
        lower_goal = goal.lower()
        assignments: List[tuple[str, str, str, Priority]] = []

        keyword_map = {
            "투자": "investment",
            "수익": "investment",
            "사업": "business",
            "전략": "business",
            "부동산": "realestate",
            "임대": "realestate",
            "세금": "tax",
            "회계": "tax",
            "법": "legal",
            "규제": "legal",
            "운영": "operations",
            "일정": "operations",
        }

        matched = set()
        for keyword, agent_key in keyword_map.items():
            if keyword in lower_goal:
                matched.add(agent_key)

        if not matched:
            matched = {"business", "operations"}

        for agent_key in sorted(matched):
            assignments.append(
                (
                    agent_key,
                    f"{self.agents[agent_key].name} 검토",
                    goal,
                    Priority.HIGH if agent_key in {"investment", "legal"} else Priority.MEDIUM,
                )
            )
        return assignments

    def run_pending_tasks(self) -> None:
        for task in self.tasks:
            if task.status == AgentStatus.DONE:
                continue

            agent = self.agents[task.assigned_agent_key]
            agent.status = AgentStatus.WORKING
            agent.current_task = task.title
            task.status = AgentStatus.WORKING

            try:
                output = self._generate_agent_output(agent, task)
                task.status = AgentStatus.DONE
                agent.status = AgentStatus.DONE
                agent.recent_result = output
                self.logs.append(
                    AssignmentLog(
                        timestamp=datetime.now().isoformat(timespec="seconds"),
                        task_id=task.id,
                        agent_key=agent.key,
                        input_text=task.detail,
                        output_text=output,
                        is_error=False,
                    )
                )
            except Exception as exc:  # broad to keep system resilient
                task.status = AgentStatus.IDLE
                agent.status = AgentStatus.IDLE
                self.logs.append(
                    AssignmentLog(
                        timestamp=datetime.now().isoformat(timespec="seconds"),
                        task_id=task.id,
                        agent_key=agent.key,
                        input_text=task.detail,
                        output_text=f"실행 실패: {exc}",
                        is_error=True,
                    )
                )

    def _generate_agent_output(self, agent: Agent, task: Task) -> str:
        templates = {
            "investment": "투자 관점 결론: 예상 리스크/수익 비율을 점검하고 단계별 투자 집행을 권장합니다.",
            "business": "사업 전략 결론: 핵심 고객/가치제안/수익모델을 1페이지 전략으로 확정하세요.",
            "realestate": "부동산 결론: 입지, 공실률, 임대수익률 기준으로 후보지를 3곳 비교하세요.",
            "tax": "세무/회계 결론: 비용증빙 체계와 분기별 세무 캘린더를 먼저 구축하세요.",
            "legal": "법무 결론: 계약서 표준 조항과 규제 체크리스트를 사전 검토하세요.",
            "operations": "운영 결론: 4주 실행 로드맵과 주간 점검 루틴을 설정하세요.",
        }
        base = templates.get(agent.key, "기본 결론: 목표를 세분화해 실행하세요.")
        return f"{base} | 작업: {task.title}"

    def save_json(self, file_path: Path) -> None:
        payload = {
            "agents": [a.__dict__ for a in self.agents.values()],
            "tasks": [
                {
                    **t.__dict__,
                    "priority": t.priority.value,
                    "status": t.status.value,
                }
                for t in self.tasks
            ],
            "logs": [l.__dict__ for l in self.logs],
        }
        file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def print_dashboard(orchestrator: Orchestrator) -> None:
    print("\n" + "=" * 72)
    print("6-에이전트 대시보드")
    print("=" * 72)
    for agent in orchestrator.agents.values():
        print(
            f"[{agent.name}] 분야={agent.domain} 상태={agent.status.value} 현재작업={agent.current_task}\n"
            f"  최근결과: {agent.recent_result}"
        )
    print("-" * 72)
    print(f"총 작업 수: {len(orchestrator.tasks)} | 로그 수: {len(orchestrator.logs)}")


def main() -> None:
    orchestrator = Orchestrator.default()

    while True:
        print_dashboard(orchestrator)
        print("\n메뉴: 1) 목표입력 2) 실행 3) 저장 4) 종료")
        choice = input("선택> ").strip()

        if choice == "1":
            goal = input("프로젝트 목표를 입력하세요> ").strip()
            try:
                orchestrator.add_project_goal(goal)
                print("작업 할당 완료")
            except ValueError as exc:
                print(f"입력 오류: {exc}")
        elif choice == "2":
            orchestrator.run_pending_tasks()
            print("실행 완료")
        elif choice == "3":
            path_text = input("저장 파일명(기본: dashboard_state.json)> ").strip() or "dashboard_state.json"
            orchestrator.save_json(Path(path_text))
            print(f"저장 완료: {path_text}")
        elif choice == "4":
            print("종료합니다.")
            break
        else:
            print("올바른 번호를 선택하세요.")


if __name__ == "__main__":
    main()
