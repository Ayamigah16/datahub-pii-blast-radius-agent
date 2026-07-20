"""The differentiator: classify each downstream asset as still exposing raw
PII, or as aggregated/derived enough that it no longer requires remediation.

This is the part a plain lineage-tag-propagation script can't do -- it reads
the asset's description and reasons about aggregation level instead of
blindly flagging everything reachable downstream.

Runs on Claude via a direct Anthropic API key by default, falling back to
Mistral's API if the Anthropic call fails (rate limit, auth issue, or any
other API-level error) -- resilience against the primary path breaking
mid-demo, not a workaround for an access problem. Both paths force a tool
call for the verdict rather than asking for JSON in free text: smaller/
cheaper models don't reliably follow a "respond with strict JSON"
instruction, but a forced tool call always returns structured output.
"""

import json
from dataclasses import dataclass
from typing import Literal

from anthropic import Anthropic, APIStatusError
from mistralai.client import Mistral

from .config import Config
from .trace import DownstreamAsset

Verdict = Literal["raw_exposure", "no_action_aggregated", "unclear_needs_review"]

_SYSTEM_PROMPT = """You are reviewing data assets downstream of a column that \
contains personal data, as part of handling a data-subject deletion request.

For each asset, decide:
- "raw_exposure": the asset still contains or directly exposes the individual's \
personal data (e.g. a row-level table, a dashboard filtered to individual records).
- "no_action_aggregated": the asset only contains aggregated or derived data where \
the individual is no longer identifiable (e.g. a daily count, a model trained on \
millions of rows with no per-person output).
- "unclear_needs_review": you cannot tell from the available metadata and a human \
should check.

Classify the asset by calling the classify_asset tool."""

_PARAMETERS = {
    "type": "object",
    "properties": {
        "verdict": {
            "type": "string",
            "enum": ["raw_exposure", "no_action_aggregated", "unclear_needs_review"],
        },
        "rationale": {"type": "string", "description": "One sentence explaining the verdict."},
    },
    "required": ["verdict", "rationale"],
}


@dataclass
class Classification:
    asset: DownstreamAsset
    verdict: Verdict
    rationale: str


def classify_asset(
    anthropic_client: Anthropic,
    mistral_client: Mistral,
    config: Config,
    asset: DownstreamAsset,
    source_column: str,
) -> Classification:
    try:
        return _classify_with_anthropic(anthropic_client, config, asset, source_column)
    except APIStatusError:
        return _classify_with_mistral(mistral_client, config, asset, source_column)


def _user_prompt(asset: DownstreamAsset, source_column: str) -> str:
    return (
        f"Source column with personal data: {source_column}\n"
        f"Downstream asset: {asset.name} ({asset.entity_type})\n"
        f"Description: {asset.description or '(none provided)'}\n"
        "Classify this asset."
    )


def _classify_with_anthropic(
    client: Anthropic, config: Config, asset: DownstreamAsset, source_column: str
) -> Classification:
    message = client.messages.create(
        model=config.anthropic_model,
        max_tokens=300,
        system=_SYSTEM_PROMPT,
        tools=[
            {
                "name": "classify_asset",
                "description": "Record the classification for this downstream asset.",
                "input_schema": _PARAMETERS,
            }
        ],
        tool_choice={"type": "tool", "name": "classify_asset"},
        messages=[{"role": "user", "content": _user_prompt(asset, source_column)}],
    )
    for block in message.content:
        if block.type == "tool_use":
            return Classification(asset=asset, verdict=block.input["verdict"], rationale=block.input["rationale"])
    raise ValueError("Anthropic response contained no tool_use block")


def _classify_with_mistral(
    client: Mistral, config: Config, asset: DownstreamAsset, source_column: str
) -> Classification:
    response = client.chat.complete(
        model=config.mistral_model,
        max_tokens=300,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _user_prompt(asset, source_column)},
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "classify_asset",
                    "description": "Record the classification for this downstream asset.",
                    "parameters": _PARAMETERS,
                },
            }
        ],
        tool_choice={"type": "function", "function": {"name": "classify_asset"}},
    )
    tool_calls = response.choices[0].message.tool_calls
    if not tool_calls:
        raise ValueError("Mistral response contained no tool call")
    arguments = tool_calls[0].function.arguments
    payload = json.loads(arguments) if isinstance(arguments, str) else arguments
    return Classification(asset=asset, verdict=payload["verdict"], rationale=payload["rationale"])
