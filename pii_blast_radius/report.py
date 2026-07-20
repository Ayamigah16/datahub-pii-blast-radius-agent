"""Builds the human-readable checklist a compliance reviewer actually uses --
this, not the write-back call, is the artifact judges should evaluate."""

from .reason import Classification

VERDICT_LABEL = {
    "raw_exposure": "ACTION NEEDED",
    "no_action_aggregated": "no action (aggregated)",
    "unclear_needs_review": "needs human review",
}


def build_checklist(subject_id: str, source_column: str, classifications: list[Classification]) -> str:
    lines = [
        f"# DSR Checklist -- subject `{subject_id}`",
        "",
        f"Source column: `{source_column}`",
        f"Downstream assets evaluated: {len(classifications)}",
        "",
    ]

    action_needed = [c for c in classifications if c.verdict == "raw_exposure"]
    no_action = [c for c in classifications if c.verdict == "no_action_aggregated"]
    needs_review = [c for c in classifications if c.verdict == "unclear_needs_review"]

    lines.append(f"- {len(action_needed)} action needed")
    lines.append(f"- {len(no_action)} no action (aggregated, not personally identifiable)")
    lines.append(f"- {len(needs_review)} needs human review")
    lines.append("")

    for group_name, group in (
        ("Action needed", action_needed),
        ("Needs human review", needs_review),
        ("No action", no_action),
    ):
        if not group:
            continue
        lines.append(f"## {group_name}")
        for c in group:
            lines.append(f"- **{c.asset.name}** (`{c.asset.urn}`) -- {c.rationale}")
        lines.append("")

    return "\n".join(lines)
