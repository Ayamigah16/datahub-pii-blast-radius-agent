# PII Blast-Radius Agent

Traces a data-subject request (GDPR/CCPA deletion or access request) through
DataHub's lineage graph, judges which downstream assets still expose the
person's raw data versus which are aggregated enough to be out of scope, and
writes the finding back onto each asset so a compliance reviewer inherits a
checklist instead of re-deriving one by hand.

See [project-brief.md](project-brief.md) for the problem statement, category
rationale (Theme 1: Agents That Do Real Work), and why this goes beyond
lineage-tag-propagation or Analytics Agent's existing write-back.
[submission-description.md](submission-description.md) is the Devpost text
description; [demo-script.md](demo-script.md) is the shot-by-shot script for
the 3-minute demo video.

## How it uses DataHub

Connects as an MCP client to the official [DataHub MCP Server](https://github.com/acryldata/mcp-server-datahub):

- `get_lineage` / `get_entities` to trace downstream from a PII-tagged column
- an LLM classification step (not a DataHub tool) to judge raw-exposure vs. aggregated
- `add_tags` / `update_description` to write the finding back onto each asset

Verified end-to-end against a live `datahub docker quickstart` instance with
the `showcase-ecommerce` datapack loaded, not just against docs. Three things
that weren't obvious going in, in case you extend this:

- **Tags must already exist as entities before `add_tags` can apply them** --
  DataHub rejects a tag URN that hasn't been created yet. `setup_demo.py`
  creates the `dsr-*` status tags plus its own `pii-data` tag via a direct
  GraphQL `createTag` call (the MCP server has no `create_tag` tool). Earlier
  this reused `showcase-ecommerce`'s bundled PII tag instead, but that tag is
  namespaced with a random-looking prefix generated fresh on every datapack
  load (`urn:li:tag:b2fd91.PII_Data` was specific to one load) -- hardcoding
  it broke on the very next reload, so this project creates its own tag
  instead of depending on datapack internals.
- **Column-level tags/descriptions live under `editableSchemaMetadata`, not
  `schemaMetadata`** -- the latter is the raw ingested aspect; user/agent edits
  go into the former. If you're spot-checking write-backs via GraphQL
  directly, query `editableSchemaMetadata`.
- **`session.call_tool()` doesn't raise on a tool-level failure** -- it
  returns a result with `isError=True` and the error in `.content`. Every
  call in this project goes through `mcp_client.call_tool_checked()`, which
  raises properly; this bit us once when a failed `add_tags` call printed a
  success message anyway.

`trace.py`'s `_parse_entity` still guesses at a couple of nested field paths
(`properties.name`, `editableProperties.description`) defensively rather than
from one confirmed shape -- worth double-checking against a real response for
entity types beyond Dataset (dashboards, ML models) if you hit empty names/descriptions.

## Setup

0. Create and activate a virtualenv (Ubuntu's system Python is externally
   managed, so `pip install` needs one). Do this once, then re-run the
   `source` step in every new terminal before using `datahub` or running
   anything in this repo:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # re-run this in every new terminal
   pip install --upgrade pip
   ```

1. Install the DataHub CLI and start DataHub locally, then load a demo dataset
   with real cross-platform lineage. The `datahub` CLI is a separate program
   from this project's own code -- it doesn't read `.env`, so it needs
   `DATAHUB_GMS_URL` exported directly in every new terminal:

   ```bash
   pip install acryl-datahub
   datahub docker quickstart
   # UI at http://localhost:9002, login datahub / datahub
   export DATAHUB_GMS_URL=http://localhost:8080   # required for every `datahub ...` command below
   datahub datapack load showcase-ecommerce
   ```

2. Install this project's dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Classification runs on Claude via **AWS Bedrock**, not a plain Anthropic
   API key. In the AWS Console, go to Bedrock -> Model access and request
   access to the Anthropic models (usually instant, but not guaranteed --
   sandbox/training accounts can have org policies blocking premium models
   regardless of the request), then copy the exact model ID from the Bedrock
   model catalog -- if it's a newer model, you likely need the cross-region
   inference profile ID (`eu.anthropic....` / `us.anthropic....`) rather than
   the bare model ID, or invocation fails with "on-demand throughput isn't
   supported." Copy `.env.example` to `.env` (this project loads it
   automatically via `python-dotenv`) and fill in `AWS_REGION` and
   `BEDROCK_MODEL_ID`; AWS credentials themselves come from the normal boto3
   chain (`aws sso login`, `~/.aws/credentials`, or env vars), not from
   `.env`. Local DataHub quickstart doesn't enable GMS auth by default, so
   `DATAHUB_GMS_TOKEN` can stay blank unless you've turned on
   `METADATA_SERVICE_AUTH_ENABLED`.

   If Bedrock access never comes through, the agent automatically falls back
   to Mistral's API on a Bedrock permission error -- get a free key at
   console.mistral.ai (phone verification, no card) and set `MISTRAL_API_KEY`
   in `.env`. Not required unless the fallback actually triggers.

4. Find a real dataset URN to point at -- URNs from `showcase-ecommerce`
   aren't predictable ahead of time (they're namespaced with a random-looking
   prefix per load), so search for one (same terminal as step 1, so
   `DATAHUB_GMS_URL` is still exported; open a new terminal, re-export it first):

   ```bash
   datahub search query "customer"   # grep the output for a urn:li:dataset:(...) you recognize
   datahub dataset get --urn "<that urn>"   # confirm it has a PII-ish column, e.g. an email field
   ```

5. Tag that column as PII and create the `dsr-*` status tags:

   ```bash
   PYTHONPATH=. python scripts/setup_demo.py --dataset-urn "<customers table urn>" --column cust_email
   ```

6. Run a data-subject request:

   ```bash
   PYTHONPATH=. python -m pii_blast_radius.cli \
     --source-urn "<customers table urn>" \
     --source-column cust_email \
     --subject-id subj_48213 \
     --output examples/sample_checklist.md
   ```

`examples/sample_checklist.md` holds real output from an actual run against
the `showcase-ecommerce` datapack (12 downstream assets traced from a tagged
`cust_email` column) -- re-run step 6 to regenerate it if you reload the
datapack, since URNs and lineage aren't guaranteed identical between loads.

## Project structure

```text
pii_blast_radius/
  mcp_client.py   connects to the DataHub MCP server
  trace.py        downstream lineage traversal
  reason.py        raw-exposure vs. aggregated classification (the differentiator)
  writeback.py    writes findings back onto flagged assets
  report.py        builds the human-readable checklist
  cli.py          wires it together end-to-end
scripts/
  setup_demo.py   one-time demo data setup (tags a PII column)
examples/
  sample_checklist.md   sample output artifact
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
