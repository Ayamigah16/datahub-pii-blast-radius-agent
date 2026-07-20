# Contributing to datahub-project/datahub-skills

**Submitted:** <https://github.com/datahub-project/datahub-skills/pull/43>
(the "validate-conventional-commit-title" check passed; the rest of this
file is the plan as drafted before opening it, kept for reference).

## Target repo

https://github.com/datahub-project/datahub-skills

## What changes

1. **New file:** `skills/datahub-lineage/templates/compliance-impact-analysis.template.md`
   (content in `compliance-impact-analysis.template.md` in this folder)
2. **Edit:** `skills/datahub-lineage/SKILL.md`
   - Insert the new `### Compliance impact analysis (data-subject requests)`
     subsection (content in `skill-md-addition.md` in this folder) between
     the existing `### Impact analysis format` and `### Cross-platform view`
     subsections.
   - Add one row to the existing "Reference Documents" table:
     `| Compliance impact analysis template | \`templates/compliance-impact-analysis.template.md\` | GDPR/CCPA data-subject-request impact analysis |`

## Why this fits here rather than as a new top-level skill

`datahub-skills` structures its skills by broad capability (Search, Enrich,
Lineage, Quality, Setup) each covering many related tasks -- not as a
registry of individual example projects. A GDPR/CCPA data-subject request is
a specific *workflow* within the lineage/impact-analysis capability the
`datahub-lineage` skill already owns (it already has an impact-analysis
template and format), not a distinct capability of its own. Proposing a new
top-level skill would duplicate most of `datahub-lineage`'s existing
traversal logic for no real benefit.

## PR details

- **Branch:** `feat/compliance-impact-analysis-template`
- **Title (Conventional Commits, enforced by their CI):**
  `feat: add compliance impact analysis template to datahub-lineage skill`
- **Body draft:**

  > While building an agent for the "Build with DataHub" hackathon that
  > handles GDPR/CCPA data-subject requests, I found `datahub-lineage`'s
  > existing impact-analysis format doesn't quite fit this use case -- it
  > answers "what's downstream" (a structural question) but a
  > data-subject request needs "what downstream still exposes this
  > specific person's data" (a judgment question: row-level exposure vs.
  > safely aggregated). This adds a compliance-specific template and a
  > short workflow section covering that distinction, alongside the
  > existing impact-analysis template rather than replacing it.
  >
  > Context: [repo link] -- the hackathon project this pattern came from.

## Before submitting, confirm

- [ ] Read through both drafted files once more for tone/accuracy
- [ ] Decide whether to link the hackathon repo in the PR body (recommended --
      shows the pattern was validated against a real working agent, not
      theoretical)
- [ ] OK to fork datahub-project/datahub-skills and open this PR under your
      GitHub account (Ayamigah16)?
