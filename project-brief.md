# Project Brief — PII Blast-Radius Agent (working name)

## One-liner
An agent that, given a data-subject request (deletion/access), traces exactly which DataHub-cataloged tables, dashboards, and ML features actually contain or derive from that person's PII — and writes remediation status back onto those assets — so compliance teams stop manually chasing lineage by hand.

## Problem
GDPR/CCPA-style data-subject requests require finding every place a person's data lives or was derived into, across warehouses, BI tools, and ML features. Today this is done manually or via naive "grep for PII tags," which over-flags aggregated/anonymized data and buries compliance teams in false positives. This is a real, expensive, recurring cost for any org with a data platform.

## Category: Agents That Do Real Work (Theme 1)
Not Open/Wildcard, despite "regulatory automation" appearing as a Theme 4 example — category is determined by function, not by which example list mentions the domain. This agent reads DataHub to understand what's connected to what, takes action (decides scope, judges false positives), and writes results back so the next reviewer inherits the finding. That's Theme 1's definition, and the submission text should say so explicitly.

## What makes this more than a re-wrap
Verified directly (not assumed): DataHub Core (open source) has **no lineage-based
tag/metadata propagation at all** — that automation (PII tags on a source column
auto-flowing to every downstream column) is a DataHub Cloud-exclusive feature,
absent from the OSS platform this hackathon requires building on. The only
PII-adjacent OSS capability, `acryl-datahub-classify` (auto-classify at
ingestion), is deprecated and Snowflake-only, and doesn't trace lineage or
produce a remediation checklist. So this isn't rebuilding an existing feature —
it's filling a real gap in the open-source stack. Two things make it more than
a mechanical lineage query, though:

1. **Judgment, not just propagation.** A naive approach tags every downstream node reachable from a PII column. The agent's actual value is reasoning over column descriptions and aggregation level to distinguish "raw PII exposure" from "aggregated data that's no longer personally identifiable," cutting false positives a blunt tag-propagation approach would generate.
2. **Write-back is the artifact, not the gimmick.** Analytics Agent already writes context back to DataHub, so that mechanism alone isn't the differentiator — the checklist and reasoning trail is. Each flagged asset gets a tag (`dsr-pending` / `dsr-no-action` / `dsr-needs-review`) plus a note explaining *why*, so a compliance reviewer can audit the agent's judgment, not just its output.

## How it uses DataHub
- **Source signal:** existing PII/sensitivity tags and glossary terms on source columns (tag or add these on the demo dataset as setup).
- **Traversal:** downstream lineage via the **MCP Server** (or Agent Context Kit) — tables → dbt models → dashboards → ML features that derive from a tagged column.
- **Reasoning:** LLM pass over each candidate asset's column descriptions/glossary context to classify raw-exposure vs. aggregated/anonymized, reducing the flagged set.
- **Write-back:** a tag (`dsr-pending` / `dsr-no-action` / `dsr-needs-review`) plus an appended note on each in-scope asset, and an ownership-based notification using DataHub's existing ownership metadata.

## Demo dataset
`showcase-ecommerce` datapack — real cross-platform lineage (Snowflake, dbt, Looker/PowerBI, Tableau, S3) gives believable multi-hop chains from a `customers.email` column to a downstream dashboard or ML feature, which is the whole demo.

## Lean stack (avoid the earlier over-engineering mistake)
- One backend service (Python, since it's the natural fit for MCP Server / DataHub SDK / LLM calls) — skip a separate Node service, Kafka, and Kubernetes entirely; none of that is needed for a hackathon demo.
- Simple CLI or minimal web UI to trigger a request and show the resulting checklist — skip a full React dashboard unless there's time left after the core agent works.
- DataHub instance from Quickstart + the datapack, no custom infra.

## 3-minute demo script
1. (0:00–0:20) Problem framing: "A customer requests deletion. Today, finding every place their data lives is manual and error-prone."
2. (0:20–1:00) Trigger the agent with a subject's email. Show it querying DataHub lineage from the tagged source column.
3. (1:00–1:50) Show the reasoning step live: one asset gets flagged raw-exposure, another gets marked no-action with the "aggregated, not personally identifiable" rationale visible — this is the moment that proves it's not just a tag-propagation script.
4. (1:50–2:30) Show the write-back landing in DataHub — status property and note visible on the asset in the DataHub UI.
5. (2:30–3:00) Close on the checklist output and the owner notification, tie back to "this is the artifact a compliance team actually uses."

## Submission checklist (don't lose points on process)
- [ ] Public repo, Apache 2.0 license file visible at top of repo's About section
- [ ] `examples/` folder with a sample generated checklist output
- [ ] Demo video ≤ 3 min, uploaded to YouTube/Vimeo/Youku
- [ ] Working hosted demo or clear local setup instructions (repo must run consistently)
- [ ] Text description states category (Theme 1) and rationale explicitly
- [ ] If time allows: one small real contribution back to DataHub core/Skills repo for the bonus criterion
