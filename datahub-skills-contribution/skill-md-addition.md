This is the proposed insertion into `skills/datahub-lineage/SKILL.md`, to go
immediately after the existing "### Impact analysis format" subsection and
before "### Cross-platform view" (matching the file's exact heading level and
style). Diff context below shows exactly where it lands.

---

### Impact analysis format

For impact analysis, group by entity type, identify critical paths (single-dependency chains), and list affected owners. See `templates/impact-analysis.template.md` for the full template.

### Compliance impact analysis (data-subject requests)

A GDPR/CCPA deletion or access request needs a different shape of impact
analysis than a schema-change audit: the question isn't "what's downstream"
but "what downstream still exposes this specific person's data." Trace
column-level lineage from the tagged PII source column (not the whole
table -- see [Step 2: Determine Traversal Mode](#step-2-determine-traversal-mode)),
then classify each downstream entity instead of listing it flat:

- **Action needed** -- still row-level, still exposes the individual (e.g. a
  table with one row per transaction, a dashboard filtered to individual
  records).
- **No action** -- aggregated enough that the individual isn't identifiable
  (e.g. a daily rollup, a model trained on millions of rows with no
  per-person output).
- **Needs review** -- can't tell from the available metadata. Treat a
  missing description as a reason to flag for review, not a reason to
  assume either verdict -- guessing here produces the exact false positives
  (or false negatives) this analysis exists to avoid.

See `templates/compliance-impact-analysis.template.md` for the full
template. If the deployment tier supports write-back, record the verdict on
each entity (tag plus a note explaining why) so the next reviewer inherits
the finding instead of re-deriving it -- see `/datahub-enrich` for applying
tags and descriptions.

### Cross-platform view

Group by platform when lineage crosses systems:
