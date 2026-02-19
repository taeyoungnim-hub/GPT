from app.connectors.base import OpenAPIConnector
from app.config import load_sources


def build_connectors() -> list[OpenAPIConnector]:
    cfg = load_sources()
    connectors = []
    for name, source_cfg in cfg.get("sources", {}).items():
        if source_cfg.get("enabled", True):
            connectors.append(OpenAPIConnector(name=name, cfg=source_cfg))
    return connectors
