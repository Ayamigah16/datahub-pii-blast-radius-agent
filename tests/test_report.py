from pii_blast_radius.reason import Classification
from pii_blast_radius.report import build_checklist
from pii_blast_radius.trace import DownstreamAsset


def _classification(verdict: str, name: str = "some_table") -> Classification:
    asset = DownstreamAsset(urn=f"urn:li:dataset:({name})", entity_type="dataset", name=name, description="")
    return Classification(asset=asset, verdict=verdict, rationale=f"rationale for {name}")


def test_counts_each_verdict_bucket():
    classifications = [
        _classification("raw_exposure", "orders"),
        _classification("raw_exposure", "customers"),
        _classification("no_action_aggregated", "daily_summary"),
        _classification("unclear_needs_review", "mystery_dashboard"),
    ]
    checklist = build_checklist("subj_1", "email", classifications)

    assert "- 2 action needed" in checklist
    assert "- 1 no action (aggregated, not personally identifiable)" in checklist
    assert "- 1 needs human review" in checklist


def test_omits_empty_groups():
    checklist = build_checklist("subj_1", "email", [_classification("no_action_aggregated")])

    assert "## Action needed" not in checklist
    assert "## Needs human review" not in checklist
    assert "## No action" in checklist


def test_includes_subject_and_source_column():
    checklist = build_checklist("subj_42", "cust_email", [])

    assert "subj_42" in checklist
    assert "cust_email" in checklist
    assert "Downstream assets evaluated: 0" in checklist


def test_asset_line_includes_urn_and_rationale():
    checklist = build_checklist("subj_1", "email", [_classification("raw_exposure", "orders")])

    assert "**orders**" in checklist
    assert "urn:li:dataset:(orders)" in checklist
    assert "rationale for orders" in checklist
