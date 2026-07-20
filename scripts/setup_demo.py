"""One-time demo setup: loads the showcase-ecommerce datapack and tags a
customer PII column so run_dsr has something real to trace.

Usage:
    datahub docker quickstart          # start local DataHub, if not already running
    datahub datapack load showcase-ecommerce
    python scripts/setup_demo.py --dataset-urn "<urn of the customers table>" --column email
"""

import asyncio

import click
import requests

from pii_blast_radius.config import load_config
from pii_blast_radius.mcp_client import call_tool_checked, datahub_session
from pii_blast_radius.writeback import TAG_BY_VERDICT

# Tags must already exist as entities in DataHub before add_tags can apply
# them. showcase-ecommerce ships its own PII tag, but it's namespaced with a
# random-looking prefix generated fresh per datapack load (e.g.
# "urn:li:tag:b2fd91.PII_Data") -- hardcoding that prefix broke on the very
# next reload. Creating our own tag instead sidesteps depending on datapack
# internals entirely.
PII_TAG_URN = "urn:li:tag:pii-data"


@click.command()
@click.option("--dataset-urn", required=True, help="URN of the dataset containing the PII column, e.g. the customers table loaded from showcase-ecommerce.")
@click.option("--column", required=True, help="Column name to tag as PII, e.g. 'email'.")
def tag_pii_column(dataset_urn: str, column: str):
    asyncio.run(_tag(dataset_urn, column))


def _ensure_tags_exist(gms_url: str, tag_urns: set[str]) -> None:
    # The MCP server's add_tags requires tags to already exist as entities --
    # it has no create_tag tool, so this goes straight to DataHub's GraphQL
    # API (createTag) instead. createTag isn't idempotent (errors on a tag
    # that already exists), so treat that specific error as success.
    for tag_urn in tag_urns:
        tag_id = tag_urn.removeprefix("urn:li:tag:")
        response = requests.post(
            f"{gms_url}/api/graphql",
            json={
                "query": "mutation($input: CreateTagInput!) { createTag(input: $input) }",
                "variables": {
                    "input": {
                        "id": tag_id,
                        "name": tag_id,
                        "description": "Created by the PII blast-radius agent's setup script.",
                    }
                },
            },
            timeout=10,
        )
        response.raise_for_status()
        errors = response.json().get("errors")
        if errors and "already exists" not in errors[0].get("message", ""):
            raise RuntimeError(f"Failed to create tag {tag_urn}: {errors}")


async def _tag(dataset_urn: str, column: str):
    config = load_config()
    _ensure_tags_exist(config.datahub_gms_url, {PII_TAG_URN, *TAG_BY_VERDICT.values()})

    async with datahub_session(config) as session:
        await call_tool_checked(
            session,
            "add_tags",
            {
                "tag_urns": [PII_TAG_URN],
                "entity_urns": [dataset_urn],
                "column_paths": [column],
            },
        )
        print(f"Tagged {dataset_urn} column '{column}' as PII")


if __name__ == "__main__":
    tag_pii_column()
