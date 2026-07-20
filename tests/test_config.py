import pytest

from pii_blast_radius.config import Config, ConfigError


@pytest.fixture
def base_env(monkeypatch):
    # DATAHUB_GMS_URL is required in Config.__init__, so every test needs it
    # set regardless of what it's actually testing.
    monkeypatch.setenv("DATAHUB_GMS_URL", "http://localhost:8080")


def test_missing_datahub_gms_url_raises(monkeypatch):
    monkeypatch.delenv("DATAHUB_GMS_URL", raising=False)
    with pytest.raises(ConfigError):
        Config()


def test_datahub_gms_token_defaults_to_empty_string(base_env, monkeypatch):
    monkeypatch.delenv("DATAHUB_GMS_TOKEN", raising=False)
    assert Config().datahub_gms_token == ""


def test_anthropic_api_key_configured_false_when_empty(base_env, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    assert Config().anthropic_api_key_configured is False


def test_anthropic_api_key_configured_false_when_unset(base_env, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert Config().anthropic_api_key_configured is False


def test_anthropic_api_key_configured_true_when_set(base_env, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-something")
    assert Config().anthropic_api_key_configured is True


def test_anthropic_api_key_property_raises_when_unset(base_env, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        Config().anthropic_api_key


def test_anthropic_model_has_a_sensible_default(base_env, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    assert Config().anthropic_model == "claude-sonnet-5"


def test_mistral_model_has_a_sensible_default(base_env, monkeypatch):
    monkeypatch.delenv("MISTRAL_MODEL", raising=False)
    assert Config().mistral_model == "mistral-large-latest"
