# DataHub PII Blast-Radius Agent

## The problem

When a customer files a GDPR or CCPA data-subject request — "delete everything you have on me" — someone has to figure out *every* place that person's data actually lives: source tables, dbt models, BI dashboards, ML features. Today that's done by hand, or by a blunt "grep for a PII tag" script that flags anything downstream of a source column, aggregated or not. Both are slow, and the blunt version buries compliance teams in false positives on data that's already anonymized.

## What it does

Given a data-subject ID and the PII-tagged source column their data lives in, the agent:

1. Traces DataHub's lineage graph downstream from that column — across warehouses, dbt models, Looker/PowerBI dashboards, and ML features — using the official DataHub MCP Server.
2. For each downstream asset, uses Claude to judge whether it still exposes the individual's raw data, or is aggregated enough that the person is no longer identifiable. This is the core of the agent: it doesn't just propagate a tag mechanically, it reasons about aggregation level from the asset's documentation and reports "needs human review" when it genuinely can't tell — rather than guessing.
3. Writes the finding back onto each asset in DataHub as a status tag (`dsr-pending` / `dsr-no-action` / `dsr-needs-review`) plus an appended note explaining why, so the next reviewer inherits the finding instead of re-deriving it.
4. Produces a markdown checklist a compliance reviewer can act on directly.

Tested end-to-end against a real `datahub docker quickstart` instance with the `showcase-ecommerce` sample dataset: tracing from a customer's tagged email column correctly identified a Snowflake/dbt table with row-level PII as needing action, while correctly clearing an aggregated PowerBI "Geographic Measures" report as no-action — and flagged several dashboards with no description metadata as needing human review rather than guessing either way.

## Category: Agents That Do Real Work

The agent reads DataHub to understand what's connected to what, takes action (judging scope, not just listing it), and writes results back so the next person or agent inherits the knowledge — which is Theme 1's definition directly.

## Why this isn't a re-wrap of an existing feature

DataHub Core (open source) has no lineage-based tag/metadata propagation at all — that automation exists only in DataHub Cloud, not in the open-source platform this hackathon is built on. The one open-source PII feature, `acryl-datahub-classify` (auto-classification at ingestion), is deprecated, Snowflake-only, and doesn't trace lineage or produce a remediation checklist. This agent fills a real gap in the open-source stack rather than reimplementing something DataHub already ships.

## How it uses DataHub

- **MCP Server** (`get_lineage`, `get_entities`) for column-level downstream lineage tracing.
- **Tags** (`add_tags`) and **descriptions** (`update_description`, append mode — preserves existing documentation rather than overwriting it) to write findings back onto affected assets.
- Creates its own small tag taxonomy (`pii-data`, `dsr-pending`, `dsr-no-action`, `dsr-needs-review`) via DataHub's GraphQL API rather than depending on any specific sample dataset's own tags.

## Platform

A local backend agent (Python CLI), not a hosted web app — there's no live URL to click into. Intended platform: Linux or macOS with Docker and Python 3.11+; developed and tested on Ubuntu 26.04 (WSL2), not verified on native Windows or macOS. Setup and testing instructions are in the repo's README; the demo video shows it running end-to-end.

## Technologies

- Python, DataHub MCP Server (`mcp-server-datahub`), Model Context Protocol (`mcp`)
- Claude via a direct Anthropic API key for the reasoning/classification step, with an automatic fallback to Mistral's API if that call fails (tested and working — both paths force a tool call for structured output rather than parsing free-text JSON, which is what actually made classification reliable)
- DataHub open-source platform (`datahub docker quickstart`), `showcase-ecommerce` sample datapack (real cross-platform lineage across Snowflake, dbt, Looker, PowerBI, Tableau)

## Repo

https://github.com/Ayamigah16/datahub-pii-blast-radius-agent (Apache 2.0)
