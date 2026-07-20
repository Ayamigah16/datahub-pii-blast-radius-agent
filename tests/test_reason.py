from unittest.mock import MagicMock

import httpx
import pytest
from anthropic import APIStatusError
from mistralai.client.errors.sdkerror import SDKError

from pii_blast_radius.config import Config
from pii_blast_radius.reason import classify_asset
from pii_blast_radius.trace import DownstreamAsset


@pytest.fixture
def config(monkeypatch):
    monkeypatch.setenv("DATAHUB_GMS_URL", "http://localhost:8080")
    return Config()


@pytest.fixture
def asset():
    return DownstreamAsset(urn="urn:li:dataset:(x)", entity_type="dataset", name="x", description="")


def _anthropic_response(verdict: str, rationale: str):
    tool_block = MagicMock(type="tool_use", input={"verdict": verdict, "rationale": rationale})
    return MagicMock(content=[tool_block])


def _mistral_response(verdict: str, rationale: str, arguments_as_string: bool = True):
    arguments = f'{{"verdict": "{verdict}", "rationale": "{rationale}"}}' if arguments_as_string else {
        "verdict": verdict,
        "rationale": rationale,
    }
    tool_call = MagicMock(function=MagicMock(arguments=arguments))
    message = MagicMock(tool_calls=[tool_call])
    return MagicMock(choices=[MagicMock(message=message)])


def _api_status_error(status_code: int) -> APIStatusError:
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    response = httpx.Response(status_code=status_code, request=request)
    return APIStatusError("boom", response=response, body=None)


def _sdk_error(status_code: int) -> SDKError:
    request = httpx.Request("POST", "https://api.mistral.ai/v1/chat/completions")
    response = httpx.Response(status_code=status_code, request=request)
    return SDKError("boom", response, "")


def test_uses_anthropic_when_key_is_configured(config, asset, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-real-key")
    anthropic_client = MagicMock()
    anthropic_client.messages.create.return_value = _anthropic_response("raw_exposure", "row-level PII")
    mistral_client = MagicMock()

    result = classify_asset(anthropic_client, mistral_client, config, asset, "email")

    assert result.verdict == "raw_exposure"
    assert result.rationale == "row-level PII"
    mistral_client.chat.complete.assert_not_called()


def test_falls_back_to_mistral_when_key_is_empty(config, asset, monkeypatch):
    # The bug this guards against: an empty (not missing) ANTHROPIC_API_KEY
    # used to make the Anthropic SDK raise a plain TypeError before any HTTP
    # call, which crashed instead of falling back.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    anthropic_client = MagicMock()
    mistral_client = MagicMock()
    mistral_client.chat.complete.return_value = _mistral_response("no_action_aggregated", "aggregated data")

    result = classify_asset(anthropic_client, mistral_client, config, asset, "email")

    assert result.verdict == "no_action_aggregated"
    anthropic_client.messages.create.assert_not_called()


def test_falls_back_to_mistral_when_anthropic_raises_api_status_error(config, asset, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-real-key")
    anthropic_client = MagicMock()
    anthropic_client.messages.create.side_effect = _api_status_error(429)
    mistral_client = MagicMock()
    mistral_client.chat.complete.return_value = _mistral_response("unclear_needs_review", "no description")

    result = classify_asset(anthropic_client, mistral_client, config, asset, "email")

    assert result.verdict == "unclear_needs_review"


def test_mistral_arguments_can_be_a_json_string_or_a_dict(config, asset, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    mistral_client = MagicMock()
    mistral_client.chat.complete.return_value = _mistral_response(
        "no_action_aggregated", "aggregated", arguments_as_string=False
    )

    result = classify_asset(MagicMock(), mistral_client, config, asset, "email")

    assert result.verdict == "no_action_aggregated"


def test_mistral_retries_on_429_then_succeeds(config, asset, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    mistral_client = MagicMock()
    mistral_client.chat.complete.side_effect = [
        _sdk_error(429),
        _mistral_response("raw_exposure", "second attempt worked"),
    ]

    from pii_blast_radius.reason import _classify_with_mistral

    result = _classify_with_mistral(mistral_client, config, asset, "email")

    assert result.verdict == "raw_exposure"
    assert mistral_client.chat.complete.call_count == 2


def test_mistral_gives_up_after_exhausting_retries_on_persistent_429(config, asset, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    mistral_client = MagicMock()
    mistral_client.chat.complete.side_effect = _sdk_error(429)

    from pii_blast_radius.reason import _classify_with_mistral

    with pytest.raises(SDKError):
        _classify_with_mistral(mistral_client, config, asset, "email", _retries=2)


def test_mistral_does_not_retry_on_a_non_rate_limit_error(config, asset, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    mistral_client = MagicMock()
    mistral_client.chat.complete.side_effect = _sdk_error(401)

    from pii_blast_radius.reason import _classify_with_mistral

    with pytest.raises(SDKError):
        _classify_with_mistral(mistral_client, config, asset, "email")
    assert mistral_client.chat.complete.call_count == 1
