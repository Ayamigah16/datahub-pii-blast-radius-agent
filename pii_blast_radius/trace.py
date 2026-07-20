"""Lineage traversal: given a PII-tagged source column, find every downstream
asset (table, dashboard, ML feature) that contains or derives from it.

Signatures verified against the installed mcp-server-datahub 0.6.0 source
(venv/lib/*/site-packages/mcp_server_datahub/tools/{lineage,entities}.py) --
NOT re-derived from docs, so these should hold across versions with the same
major version, but re-check after any mcp-server-datahub upgrade.
"""

import json
from dataclasses import dataclass

from mcp import ClientSession

from .mcp_client import call_tool_checked


@dataclass
class DownstreamAsset:
    urn: str
    entity_type: str
    name: str
    description: str


async def get_downstream_assets(
    session: ClientSession, source_urn: str, source_column: str, max_hops: int = 3
) -> list[DownstreamAsset]:
    # `column` scopes get_lineage to assets that derive from this specific
    # column, not the whole table -- this is what keeps false positives down
    # (a table can have 40 columns and only one holds this PII).
    lineage = await call_tool_checked(
        session,
        "get_lineage",
        {
            "urn": source_urn,
            "column": source_column,
            "upstream": False,
            "max_hops": max_hops,
        },
    )
    entity_urns = _extract_downstream_urns(lineage)
    if not entity_urns:
        return []

    details = await call_tool_checked(session, "get_entities", {"urns": entity_urns})
    return _to_assets(details)


def _extract_downstream_urns(lineage_result) -> list[str]:
    payload = _tool_result_json(lineage_result)
    search_results = (payload.get("downstreams") or {}).get("searchResults") or []
    return [
        item["entity"]["urn"]
        for item in search_results
        if item.get("entity", {}).get("urn")
    ]


def _to_assets(entities_result) -> list[DownstreamAsset]:
    payload = _tool_result_json(entities_result)
    entities = payload if isinstance(payload, list) else [payload]
    return [_parse_entity(entity) for entity in entities if entity]


def _parse_entity(entity: dict) -> DownstreamAsset:
    # Entity shape varies by type (Dataset/Dashboard/MLModel all nest fields
    # differently under `properties` / `editableProperties`); this checks the
    # common spots rather than assuming one fixed path. Verify against a real
    # response once GMS is up -- print(json.dumps(entity, indent=2)) in cli.py
    # -- and simplify this if one path turns out to always apply.
    properties = entity.get("properties") or {}
    editable = entity.get("editableProperties") or {}
    name = properties.get("name") or entity.get("name") or entity.get("urn", "")
    description = (
        editable.get("description")
        or properties.get("description")
        or ""
    )
    return DownstreamAsset(
        urn=entity.get("urn", ""),
        entity_type=entity.get("type", entity.get("__typename", "unknown")),
        name=name,
        description=description,
    )


def _tool_result_json(tool_result):
    for block in tool_result.content:
        if getattr(block, "type", None) == "text":
            return json.loads(block.text)
    return {}
