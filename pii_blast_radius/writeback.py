"""Writes the agent's findings back onto the DataHub assets it flagged, so the
next reviewer (human or agent) inherits the finding instead of re-deriving it.

Uses add_tags rather than add_structured_properties for the status marker --
structured properties need a schema defined in DataHub before you can set
values on one (see the io.acryl.* examples in structured_properties.py), which
is extra setup this project doesn't need. Tags require no predefinition and
show up directly in the DataHub UI, which also reads better on a 3-minute demo
video. Revisit if the richer typed-value semantics of structured properties
turn out to matter later.

Signatures verified against installed mcp-server-datahub 0.6.0 source
(mcp_server_datahub/tools/{descriptions,tags}.py).
"""

from mcp import ClientSession

from .mcp_client import call_tool_checked
from .reason import Classification

TAG_BY_VERDICT = {
    "raw_exposure": "urn:li:tag:dsr-pending",
    "no_action_aggregated": "urn:li:tag:dsr-no-action",
    "unclear_needs_review": "urn:li:tag:dsr-needs-review",
}


async def write_finding(session: ClientSession, subject_id: str, classification: Classification) -> None:
    tag_urn = TAG_BY_VERDICT[classification.verdict]

    await call_tool_checked(
        session,
        "add_tags",
        {
            "tag_urns": [tag_urn],
            "entity_urns": [classification.asset.urn],
        },
    )

    note = f"[DSR agent] subject={subject_id} verdict={classification.verdict}: {classification.rationale}"
    await call_tool_checked(
        session,
        "update_description",
        {
            "entity_urn": classification.asset.urn,
            "operation": "append",
            "description": note,
        },
    )
