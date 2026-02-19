from __future__ import annotations

from pathlib import Path
import json

CONFIG_PATH_YAML = Path("config/sources.yaml")
CONFIG_PATH_JSON = Path("config/sources.json")


def _parse_yaml_minimal(text: str) -> dict:
    """Very small YAML subset parser for this repository's config shape.

    Supports:
    - top-level mapping
    - nested mapping by indentation (2 spaces)
    - scalar strings/booleans
    """
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        key_val = line.strip()
        if ":" not in key_val:
            continue

        key, val = key_val.split(":", 1)
        key = key.strip()
        val = val.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if not val:
            node: dict = {}
            parent[key] = node
            stack.append((indent, node))
            continue

        if val.lower() == "true":
            parsed: object = True
        elif val.lower() == "false":
            parsed = False
        else:
            parsed = val.strip('"').strip("'")

        parent[key] = parsed

    return root


def load_sources() -> dict:
    if CONFIG_PATH_JSON.exists():
        with CONFIG_PATH_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)

    if CONFIG_PATH_YAML.exists():
        with CONFIG_PATH_YAML.open("r", encoding="utf-8") as f:
            return _parse_yaml_minimal(f.read())

    return {}
