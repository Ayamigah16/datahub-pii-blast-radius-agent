import os


class ConfigError(RuntimeError):
    pass


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


class Config:
    """Reads connection settings from the environment. See .env.example.

    Classification runs on Claude via AWS Bedrock (not a plain Anthropic API
    key) -- aws_region/aws_profile are required lazily, on first access,
    rather than in __init__, so scripts that only talk to DataHub
    (setup_demo.py) don't need AWS credentials just to construct this object.
    Actual AWS credentials come from the normal boto3 chain (env vars,
    ~/.aws/credentials, SSO) -- aws_profile just selects which one if you use
    named profiles.
    """

    def __init__(self):
        self.datahub_gms_url = _require("DATAHUB_GMS_URL")
        self.datahub_gms_token = os.environ.get("DATAHUB_GMS_TOKEN", "")
        self.aws_profile = os.environ.get("AWS_PROFILE") or None

    @property
    def aws_region(self) -> str:
        return _require("AWS_REGION")

    @property
    def anthropic_model(self) -> str:
        # A Bedrock model ID (e.g. "anthropic.claude-...-v1:0" or a
        # "us.anthropic.claude-..." cross-region inference profile ID) --
        # copy this exactly from the Bedrock console's model catalog, it
        # does not match the direct-API model names.
        return _require("BEDROCK_MODEL_ID")

    @property
    def mistral_api_key(self) -> str:
        # Fallback path when Bedrock model access isn't granted (e.g. a
        # sandbox account with a policy restricting premium models). Only
        # required if that fallback actually triggers -- get a free key at
        # console.mistral.ai (phone verification, no card needed).
        return _require("MISTRAL_API_KEY")

    @property
    def mistral_model(self) -> str:
        return os.environ.get("MISTRAL_MODEL", "mistral-large-latest")


def load_config() -> Config:
    return Config()
