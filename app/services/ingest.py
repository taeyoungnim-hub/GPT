import asyncio
from typing import Sequence

from app.connectors.registry import build_connectors
from app.db import get_conn
from app.models import Document


INSERT_SQL = """
INSERT INTO documents (source, title, url, published_at, region, category, summary, status)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""


async def sync_all_sources() -> dict:
    connectors = build_connectors()
    tasks = [connector.fetch() for connector in connectors]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    inserted = 0
    errors: list[str] = []

    conn = get_conn()
    try:
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"{connectors[i].name}: {result}")
                continue
            inserted += _insert_documents(conn, result)
        conn.commit()
    finally:
        conn.close()

    return {
        "sources": len(connectors),
        "inserted": inserted,
        "errors": errors,
    }


def _insert_documents(conn, docs: Sequence[Document]) -> int:
    rows = [
        (
            d.source,
            d.title,
            d.url,
            d.published_at.isoformat(),
            d.region,
            d.category,
            d.summary,
            d.status,
        )
        for d in docs
    ]
    conn.executemany(INSERT_SQL, rows)
    return len(rows)
