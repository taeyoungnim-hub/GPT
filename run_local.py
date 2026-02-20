from __future__ import annotations

import asyncio
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app.db import get_conn, init_db
from app.services.ingest import sync_all_sources
from app.services.validate import evaluate_document


HTML = """<!doctype html>
<html lang=\"ko\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
  <title>부동산 공공고시 로컬 대시보드</title>
  <style>
    body{font-family:system-ui,Arial,sans-serif;max-width:1200px;margin:18px auto;padding:0 12px;background:#f8fafc;color:#0f172a}
    .grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:12px 0}
    .card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:12px}
    .title{font-size:12px;color:#64748b}.value{font-size:26px;font-weight:700;margin-top:4px}
    .row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
    input,button,select{padding:8px;font-size:14px;border:1px solid #cbd5e1;border-radius:8px;background:white}
    button{cursor:pointer;background:#0f172a;color:white}
    button.secondary{background:#475569}
    table{width:100%;border-collapse:collapse;margin-top:12px;background:white}
    th,td{border:1px solid #e2e8f0;padding:8px;font-size:13px;text-align:left;vertical-align:top}
    pre{background:#0b1020;color:#dbeafe;padding:10px;border-radius:10px;white-space:pre-wrap;min-height:90px}
    .muted{color:#64748b;font-size:12px}
  </style>
</head>
<body>
  <h2>부동산 공공고시 통합 대시보드 (로컬 구동)</h2>
  <div class=\"muted\">공개자료 수집 → 후보 탐색 → 검증 점수화 → SOP 실행</div>

  <div class=\"grid\" id=\"overview\"></div>

  <div class=\"card\">
    <div class=\"row\">
      <button onclick=\"syncAll()\">전체 소스 동기화</button>
      <button class=\"secondary\" onclick=\"loadOverview()\">개요 새로고침</button>
      <input id=\"keyword\" placeholder=\"키워드\" value=\"도시관리계획\" />
      <input id=\"region\" placeholder=\"지역\" value=\"서울\" />
      <select id=\"limit\"><option>50</option><option selected>200</option><option>500</option></select>
      <button class=\"secondary\" onclick=\"searchDocs()\">문서 검색</button>
    </div>
    <div class=\"muted\" id=\"meta\"></div>
    <table id=\"tbl\"></table>
  </div>

  <div class=\"card\" style=\"margin-top:10px\">
    <h3 style=\"margin:0 0 8px\">실행 로그 / 검증 결과</h3>
    <pre id=\"log\"></pre>
  </div>

<script>
let rows=[];
const log=(m)=>document.getElementById('log').textContent=typeof m==='string'?m:JSON.stringify(m,null,2);

async function jget(url){const r=await fetch(url);return r.json();}
async function jpost(url){const r=await fetch(url,{method:'POST'});return r.json();}

function metric(title, val){
  return `<div class=\"card\"><div class=\"title\">${title}</div><div class=\"value\">${val}</div></div>`;
}

async function loadOverview(){
  const o=await jget('/overview');
  document.getElementById('overview').innerHTML=
    metric('총 문서', o.total_documents)+
    metric('검증 완료', o.total_validations)+
    metric('소스 수', o.sources)+
    metric('평균 점수', o.avg_score);
}

async function syncAll(){
  const res=await jpost('/sync');
  log(res);
  await loadOverview();
  await searchDocs();
}

async function searchDocs(){
  const keyword=document.getElementById('keyword').value;
  const region=document.getElementById('region').value;
  const limit=document.getElementById('limit').value;
  const q=new URLSearchParams({keyword,region,limit});
  rows=await jget('/documents?'+q.toString());
  document.getElementById('meta').textContent=`검색 결과 ${rows.length}건`;
  renderTable();
}

async function validateDoc(id){
  const res=await jpost('/validate/'+id);
  log(res);
  await loadOverview();
}

function renderTable(){
  const t=document.getElementById('tbl');
  if(!rows.length){t.innerHTML='';return;}
  const head=['id','source','title','region','status','published_at','action'];
  const trh='<tr>'+head.map(h=>`<th>${h}</th>`).join('')+'</tr>';
  const body=rows.map(r=>`<tr><td>${r.id}</td><td>${r.source}</td><td>${r.title}</td><td>${r.region}</td><td>${r.status}</td><td>${r.published_at||''}</td><td><button onclick=\"validateDoc(${r.id})\">검증</button></td></tr>`).join('');
  t.innerHTML=trh+body;
}

loadOverview();
searchDocs();
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, code: int, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self._send_html(200, HTML)
            return

        if parsed.path == "/health":
            self._send_json(200, {"ok": True, "mode": "stdlib"})
            return

        if parsed.path == "/overview":
            self._send_json(200, build_overview())
            return

        if parsed.path == "/documents":
            qs = parse_qs(parsed.query)
            keyword = qs.get("keyword", [None])[0]
            region = qs.get("region", [None])[0]
            try:
                limit = int(qs.get("limit", ["100"])[0])
            except ValueError:
                limit = 100

            sql = "SELECT * FROM documents WHERE 1=1"
            params: list[object] = []
            if keyword:
                sql += " AND (title LIKE ? OR summary LIKE ?)"
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            if region:
                sql += " AND region LIKE ?"
                params.append(f"%{region}%")
            sql += " ORDER BY published_at DESC LIMIT ?"
            params.append(min(500, max(1, limit)))

            conn = get_conn()
            conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
            try:
                docs = conn.execute(sql, params).fetchall()
            finally:
                conn.close()
            self._send_json(200, docs)
            return

        self._send_json(404, {"detail": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/sync":
            result = asyncio.run(sync_all_sources())
            self._send_json(200, result)
            return

        if parsed.path.startswith("/validate/"):
            try:
                doc_id = int(parsed.path.rsplit("/", 1)[-1])
                result = evaluate_document(doc_id).model_dump()
                self._send_json(200, result)
            except ValueError as e:
                self._send_json(404, {"detail": str(e)})
            return

        self._send_json(404, {"detail": "not found"})


def build_overview() -> dict:
    conn = get_conn()
    try:
        total_documents = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        total_validations = conn.execute("SELECT COUNT(*) FROM validations").fetchone()[0]
        sources = conn.execute("SELECT COUNT(DISTINCT source) FROM documents").fetchone()[0]
        avg_score = conn.execute("SELECT COALESCE(ROUND(AVG(score),1),0) FROM validations").fetchone()[0]
        return {
            "total_documents": total_documents,
            "total_validations": total_validations,
            "sources": sources,
            "avg_score": avg_score,
        }
    finally:
        conn.close()


def main() -> None:
    init_db()
    Path("notion_templates").mkdir(exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Serving local dashboard at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
