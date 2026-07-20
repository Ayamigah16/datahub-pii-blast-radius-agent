import json
from types import SimpleNamespace

from pii_blast_radius.trace import _extract_downstream_urns, _parse_entity, _to_assets, _tool_result_json


def _tool_result(payload) -> SimpleNamespace:
    # Mimics an MCP CallToolResult: .content is a list of blocks, and the
    # actual payload is JSON-encoded text inside a block with type "text".
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps(payload))])


def test_tool_result_json_unwraps_text_block():
    result = _tool_result_json(_tool_result({"foo": "bar"}))
    assert result == {"foo": "bar"}


def test_tool_result_json_returns_empty_dict_with_no_text_block():
    result = _tool_result_json(SimpleNamespace(content=[]))
    assert result == {}


def test_extract_downstream_urns_reads_the_downstreams_key():
    # Shape confirmed against a live get_lineage response, not guessed.
    payload = {
        "downstreams": {
            "searchResults": [
                {"entity": {"urn": "urn:li:dataset:(a)"}},
                {"entity": {"urn": "urn:li:dataset:(b)"}},
            ]
        }
    }
    urns = _extract_downstream_urns(_tool_result(payload))
    assert urns == ["urn:li:dataset:(a)", "urn:li:dataset:(b)"]


def test_extract_downstream_urns_skips_entities_without_urn():
    payload = {"downstreams": {"searchResults": [{"entity": {}}, {"entity": {"urn": "urn:li:dataset:(b)"}}]}}
    urns = _extract_downstream_urns(_tool_result(payload))
    assert urns == ["urn:li:dataset:(b)"]


def test_extract_downstream_urns_handles_missing_downstreams_key():
    assert _extract_downstream_urns(_tool_result({})) == []


def test_parse_entity_prefers_editable_description_over_properties_description():
    entity = {
        "urn": "urn:li:dataset:(x)",
        "type": "DATASET",
        "properties": {"name": "x", "description": "raw ingested description"},
        "editableProperties": {"description": "agent-edited description"},
    }
    asset = _parse_entity(entity)
    assert asset.description == "agent-edited description"
    assert asset.name == "x"


def test_parse_entity_falls_back_to_urn_when_no_name_available():
    asset = _parse_entity({"urn": "urn:li:dataset:(x)"})
    assert asset.name == "urn:li:dataset:(x)"
    assert asset.description == ""


def test_to_assets_handles_a_single_entity_dict_not_wrapped_in_a_list():
    result = _to_assets(_tool_result({"urn": "urn:li:dataset:(solo)", "type": "DATASET"}))
    assert len(result) == 1
    assert result[0].urn == "urn:li:dataset:(solo)"
