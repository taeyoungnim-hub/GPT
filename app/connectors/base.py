from __future__ import annotations

from datetime import datetime
from typing import Any
import asyncio
import json
from urllib.parse import urlencode
from urllib.request import urlopen

from app.models import Document


class OpenAPIConnector:
    def __init__(self, name: str, cfg: dict[str, Any]):
        self.name = name
        self.cfg = cfg

    async def fetch(self) -> list[Document]:
        endpoint = self.cfg.get("endpoint")
        if not endpoint:
            return self._fallback_docs()

        params = dict(self.cfg.get("params", {}))
        api_key = self.cfg.get("api_key")
        if api_key and self.cfg.get("api_key_param"):
            params[self.cfg["api_key_param"]] = api_key

        url = endpoint
        if params:
            sep = "&" if "?" in endpoint else "?"
            url = f"{endpoint}{sep}{urlencode(params)}"

        payload = await asyncio.to_thread(self._fetch_json_sync, url)
        return self._normalize(payload)

    def _fetch_json_sync(self, url: str) -> Any:
        timeout = int(self.cfg.get("timeout_sec", 20))
        with urlopen(url, timeout=timeout) as resp:  # nosec B310
            raw = resp.read().decode("utf-8", errors="ignore")
        return json.loads(raw)

    def _normalize(self, payload: Any) -> list[Document]:
        records = payload if isinstance(payload, list) else payload.get("items", [])
        out: list[Document] = []
        for item in records[: int(self.cfg.get("limit", 50))]:
            title = str(item.get(self.cfg.get("title_field", "title"), "제목없음"))
            url = str(item.get(self.cfg.get("url_field", "url"), self.cfg.get("homepage", "")))
            published = item.get(self.cfg.get("date_field", "published_at"))
            published_at = self._to_dt(published)
            out.append(
                Document(
                    source=self.name,
                    title=title,
                    url=url,
                    published_at=published_at,
                    region=str(item.get(self.cfg.get("region_field", "region"), self.cfg.get("region", "전국"))),
                    category=self.cfg.get("category", "공공자료"),
                    summary=str(item.get(self.cfg.get("summary_field", "summary"), "")),
                    status=self.cfg.get("status", "공고"),
                )
            )
        return out

    def _to_dt(self, value: Any) -> datetime:
        if not value:
            return datetime.utcnow()
        if isinstance(value, (int, float)):
            return datetime.utcfromtimestamp(value)
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return datetime.utcnow()

    def _fallback_docs(self) -> list[Document]:
        return [
            Document(
                source=self.name,
                title=f"[{self.name}] 설정 필요: endpoint/api_key",
                url=self.cfg.get("homepage", ""),
                published_at=datetime.utcnow(),
                region=self.cfg.get("region", "전국"),
                category=self.cfg.get("category", "공공자료"),
                summary="sources.yaml/json에 endpoint/파라미터를 입력하면 자동 수집됩니다.",
                status=self.cfg.get("status", "공고"),
            )
        ]
