# Demo video script (target: 2:45, hard cap 3:00)

Judges aren't required to watch past 3 minutes, so the "wow" moment (the reasoning step) has to land before 2:00, not at the end.

## Recording setup

- DataHub UI open at `http://localhost:9002`, logged in, `customers` dataset page open in one tab.
- Terminal open in the project root, venv activated, ready to run the CLI command.
- Have `examples/sample_checklist.md` open in an editor tab, ready to flip to.

---

**0:00 -- 0:15 | Problem (talking head or voiceover over a blank slide)**

> "When a customer asks a company to delete their data under GDPR or CCPA, someone has to find every place that data actually lives -- source tables, dashboards, ML features. Today that's manual, or a blunt script that flags everything downstream and buries compliance teams in false positives."

**0:15 -- 0:35 | Show the starting point (DataHub UI)**

- Screen: the `customers` table in DataHub, scroll to the `cust_email` column, show the `PII_Data` tag already on it.
- Narration: "This is DataHub's lineage graph for an e-commerce platform -- real cross-platform lineage across Snowflake, dbt, Looker, and PowerBI. The customer's email column is tagged PII. Everything downstream of it is where their data could still live."

**0:35 -- 1:00 | Trigger the agent (terminal)**

- Run: `python -m pii_blast_radius.cli --source-urn "..." --source-column cust_email --subject-id subj_48213 --output examples/sample_checklist.md`
- Let "Found 12 downstream assets from ..." print on screen.
- Narration: "The agent traces DataHub's lineage graph from that column, using the official DataHub MCP Server -- not a hardcoded list, a live query."

**1:00 -- 1:50 | The differentiator: judgment, not propagation (this is the beat that matters most)**

- Cut to two side-by-side results from the real run:
  - `order_details` (dbt/Snowflake) -- flagged **action needed**: contains row-level PII, one row per order line item.
  - `Geographic Measures` (PowerBI) -- flagged **no action**: aggregated by region, not personally identifiable.
- Narration: "A naive approach would flag both -- they're both downstream of the email column. The agent reasons about aggregation level instead: one is row-level customer data, the other is a regional rollup. It also knows when it doesn't know -- several dashboards here got flagged 'needs human review' because they had no documentation to reason from, instead of guessing either way."

**1:50 -- 2:25 | Write-back lands in DataHub (UI)**

- Switch to DataHub UI, `order_details` asset page: show the `dsr-pending` tag now present, and the appended note in the description (scroll to show it's appended to the existing documentation, not overwriting it).
- Narration: "The finding gets written back onto the asset itself -- a status tag and a note explaining why. The next reviewer, or the next agent, inherits this instead of re-deriving it from scratch."

**2:25 -- 2:45 | The actual deliverable (checklist)**

- Switch to `examples/sample_checklist.md`: scroll through the action-needed / needs-review / no-action sections.
- Narration: "This is what a compliance reviewer actually works from -- a checklist, not a raw graph dump."

**2:45 -- 3:00 | Close**

> "Built entirely on DataHub's open-source stack -- the MCP Server for lineage, tags and descriptions for write-back. Not a wrapper around an existing feature: DataHub Core has no lineage-based tag propagation at all, that's a Cloud-only feature. This fills a real gap, for a problem every data platform team with customers in the EU or California actually has."

---

## Shot list checklist

- [ ] DataHub UI: `cust_email` column with `PII_Data` tag
- [ ] Terminal: CLI command + "Found N downstream assets" output
- [ ] Split/cut: `order_details` (action needed) vs `Geographic Measures` (no action) rationale text
- [ ] DataHub UI: `order_details` asset showing `dsr-pending` tag + appended note
- [ ] `examples/sample_checklist.md` scrolled through
- [ ] Closing line on category fit / originality

## Recording notes

- Do a dry run of the CLI command before recording -- if any asset's classification comes back differently than the checklist committed to the repo (data can drift if you re-load the datapack), pick whichever two contrasting examples are cleanest for the 1:00-1:50 beat rather than forcing a re-take to match exactly.
- Keep terminal font large enough to read on a compressed YouTube upload.
