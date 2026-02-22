from pathlib import Path

from agent_dashboard import AgentStatus, Orchestrator


def test_default_agents_count():
    o = Orchestrator.default()
    assert len(o.agents) == 6


def test_add_goal_creates_tasks():
    o = Orchestrator.default()
    o.add_project_goal("부동산 투자 전략 만들기")
    assert len(o.tasks) >= 2


def test_run_tasks_and_logs(tmp_path: Path):
    o = Orchestrator.default()
    o.add_project_goal("사업 운영 일정")
    o.run_pending_tasks()

    assert all(t.status == AgentStatus.DONE for t in o.tasks)
    assert len(o.logs) == len(o.tasks)

    out_file = tmp_path / "state.json"
    o.save_json(out_file)
    assert out_file.exists()
