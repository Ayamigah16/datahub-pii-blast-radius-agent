from pii_blast_radius.writeback import TAG_BY_VERDICT


def test_every_verdict_has_a_tag():
    # reason.py's Verdict literal has exactly these three values -- if that
    # ever changes without updating this mapping, write_finding would raise
    # a KeyError on the new verdict at write-back time.
    assert set(TAG_BY_VERDICT.keys()) == {"raw_exposure", "no_action_aggregated", "unclear_needs_review"}


def test_tags_are_unique_and_namespaced():
    tags = list(TAG_BY_VERDICT.values())
    assert len(tags) == len(set(tags)), "two verdicts must not share a tag"
    assert all(tag.startswith("urn:li:tag:dsr-") for tag in tags)
