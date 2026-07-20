import os

from dotenv import load_dotenv

# Loads .env into the environment on first import of this module. Without
# this, .env sits on disk unread and every entrypoint needs its variables
# exported by hand first -- which is how this project was actually tested
# during development, and not what the README tells a fresh user to do.
load_dotenv()


class ConfigError(RuntimeError):
    pass


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


class Config:
    """Reads connection settings from the environment. See .env.example.

    anthropic_api_key / mistral_api_key are required lazily, on first access,
    rather than in __init__, so scripts that only talk to DataHub
    (setup_demo.py) don't need either key just to construct this object.

    Deliberately NOT using AWS Bedrock: a sandbox/training AWS account's org
    policy for external use (e.g. a hackathon submission) can't be verified
    from here, so this uses a personal Anthropic API key directly instead --
    no third-party org's terms to worry about. Mistral remains as a fallback
    for resilience, not because of any access-grant uncertainty on this path.
    """

    def __init__(self):
        self.datahub_gms_url = _require("DATAHUB_GMS_URL")
        self.datahub_gms_token = os.environ.get("DATAHUB_GMS_TOKEN", "")

    @property
    def anthropic_api_key(self) -> str:
        return _require("ANTHROPIC_API_KEY")

    @property
    def anthropic_api_key_configured(self) -> bool:
        # An empty (not missing) key makes the Anthropic SDK raise a plain
        # TypeError at request-build time, before any HTTP call -- unlike an
        # invalid-but-present key, which fails server-side with a catchable
        # APIStatusError. classify_asset checks this first so an unset key
        # falls back to Mistral cleanly instead of crashing.
        return bool(os.environ.get("ANTHROPIC_API_KEY"))

    @property
    def anthropic_model(self) -> str:
        return os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

    @property
    def mistral_api_key(self) -> str:
        # Fallback path if the Anthropic API key is unavailable or rate
        # limited. Only required if that fallback actually triggers -- get a
        # free key at console.mistral.ai (phone verification, no card needed).
        return _require("MISTRAL_API_KEY")

    @property
    def mistral_model(self) -> str:
        return os.environ.get("MISTRAL_MODEL", "mistral-large-latest")


def load_config() -> Config:
    return Config()
