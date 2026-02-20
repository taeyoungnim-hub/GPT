from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Document:
    source: str
    title: str
    url: str
    published_at: datetime
    region: str = "전국"
    category: str = "기타"
    summary: str = ""
    status: str = "공고"


@dataclass
class ValidationResult:
    document_id: int
    score: float
    rationale: list[str]
    demand_signal: int
    policy_signal: int
    transit_signal: int
    stakeholder_signal: int

    def model_dump(self) -> dict:
        return asdict(self)
