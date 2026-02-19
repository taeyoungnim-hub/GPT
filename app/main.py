from fastapi import FastAPI, Query, HTTPException

from app.db import init_db, get_conn
from app.services.ingest import sync_all_sources
from app.services.validate import evaluate_document

app = FastAPI(title="부동산 공공고시 수집 대시보드 API")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/sync")
async def sync() -> dict:
    return await sync_all_sources()


@app.get("/documents")
def documents(
    keyword: str | None = Query(default=None),
    region: str | None = Query(default=None),
    limit: int = Query(default=100, le=500),
) -> list[dict]:
    sql = "SELECT * FROM documents WHERE 1=1"
    params: list[str | int] = []

    if keyword:
        sql += " AND (title LIKE ? OR summary LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    if region:
        sql += " AND region LIKE ?"
        params.append(f"%{region}%")

    sql += " ORDER BY published_at DESC LIMIT ?"
    params.append(limit)

    conn = get_conn()
    conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


@app.post("/validate/{document_id}")
def validate(document_id: int):
    try:
        return evaluate_document(document_id).model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
