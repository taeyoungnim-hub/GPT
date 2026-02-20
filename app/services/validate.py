import json
from app.db import get_conn
from app.models import ValidationResult


def evaluate_document(document_id: int) -> ValidationResult:
    conn = get_conn()
    conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    try:
        row = conn.execute("SELECT * FROM documents WHERE id=?", (document_id,)).fetchone()
        if not row:
            raise ValueError("document not found")

        text = " ".join([row["title"], row.get("summary", ""), row.get("category", "")]).lower()

        demand_signal = _score(text, ["주택", "산업단지", "재개발", "재건축", "상권", "택지"], 25)
        policy_signal = _score(text, ["결정고시", "도시관리계획", "변경", "승인", "지구단위"], 25)
        transit_signal = _score(text, ["철도", "역", "도로", "gtx", "환승", "교통"], 25)
        stakeholder_signal = _score(text, ["민간", "공공", "사업시행자", "조합", "협의"], 25)

        score = demand_signal + policy_signal + transit_signal + stakeholder_signal
        rationale = [
            f"수요신호: {demand_signal}",
            f"정책신호: {policy_signal}",
            f"교통신호: {transit_signal}",
            f"이해관계자신호: {stakeholder_signal}",
        ]

        result = ValidationResult(
            document_id=document_id,
            score=score,
            rationale=rationale,
            demand_signal=demand_signal,
            policy_signal=policy_signal,
            transit_signal=transit_signal,
            stakeholder_signal=stakeholder_signal,
        )

        conn.execute(
            """
            INSERT INTO validations
                (document_id, score, rationale, demand_signal, policy_signal, transit_signal, stakeholder_signal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(document_id) DO UPDATE SET
                score=excluded.score,
                rationale=excluded.rationale,
                demand_signal=excluded.demand_signal,
                policy_signal=excluded.policy_signal,
                transit_signal=excluded.transit_signal,
                stakeholder_signal=excluded.stakeholder_signal,
                updated_at=CURRENT_TIMESTAMP
            """,
            (
                result.document_id,
                result.score,
                json.dumps(result.rationale, ensure_ascii=False),
                result.demand_signal,
                result.policy_signal,
                result.transit_signal,
                result.stakeholder_signal,
            ),
        )
        conn.commit()
        return result
    finally:
        conn.close()


def _score(text: str, keywords: list[str], max_score: int) -> int:
    hits = sum(1 for k in keywords if k in text)
    if hits == 0:
        return 0
    return min(max_score, hits * (max_score // 3 or 1))
