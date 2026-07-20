import asyncio
import os

import click
from anthropic import Anthropic
from mistralai.client import Mistral

from .config import load_config
from .mcp_client import datahub_session
from .reason import classify_asset
from .report import VERDICT_LABEL, build_checklist
from .trace import get_downstream_assets
from .writeback import write_finding


@click.command()
@click.option("--source-urn", required=True, help="URN of the PII-tagged source column's dataset.")
@click.option("--source-column", required=True, help="Name of the column containing the subject's personal data.")
@click.option("--subject-id", required=True, help="Identifier for the data subject making the request.")
@click.option("--output", default="dsr_checklist.md", help="Where to write the markdown checklist.")
@click.option("--dry-run", is_flag=True, help="Skip writing findings back to DataHub; report only.")
def run_dsr(source_urn: str, source_column: str, subject_id: str, output: str, dry_run: bool):
    """Trace a data-subject request through DataHub lineage, classify each
    downstream asset, write the finding back, and print a checklist."""
    asyncio.run(_run(source_urn, source_column, subject_id, output, dry_run))


async def _run(source_urn: str, source_column: str, subject_id: str, output: str, dry_run: bool):
    config = load_config()
    # Neither client requires its key to be present at construction time --
    # Mistral is only a fallback if the Anthropic call fails, so neither
    # ANTHROPIC_API_KEY nor MISTRAL_API_KEY is required here unless the
    # corresponding path is actually used (see reason.py).
    anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    mistral_client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))

    async with datahub_session(config) as session:
        assets = await get_downstream_assets(session, source_urn, source_column)
        click.echo(f"Found {len(assets)} downstream assets from {source_urn}\n")

        classifications = []
        for i, asset in enumerate(assets, start=1):
            classification = classify_asset(anthropic_client, mistral_client, config, asset, source_column)
            classifications.append(classification)
            click.echo(f"[{i}/{len(assets)}] {asset.name}: {VERDICT_LABEL[classification.verdict]}")

        if not dry_run:
            click.echo("\nWriting findings back to DataHub...")
            for classification in classifications:
                await write_finding(session, subject_id, classification)

    checklist = build_checklist(subject_id, source_column, classifications)
    with open(output, "w") as f:
        f.write(checklist)
    click.echo(f"Wrote checklist to {output}")


if __name__ == "__main__":
    run_dsr()
