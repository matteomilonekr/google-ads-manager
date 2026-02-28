"""Google Ads OAuth2 authentication and client initialization."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from google.ads.googleads.client import GoogleAdsClient

from google_ads_mcp.utils.errors import AuthenticationError

_REQUIRED_ENV_VARS = {
    "GOOGLE_ADS_DEVELOPER_TOKEN": "developer_token",
    "GOOGLE_ADS_CLIENT_ID": "client_id",
    "GOOGLE_ADS_CLIENT_SECRET": "client_secret",
    "GOOGLE_ADS_REFRESH_TOKEN": "refresh_token",
}

_OPTIONAL_ENV_VARS = {
    "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "login_customer_id",
}


@dataclass(frozen=True)
class GoogleAdsConfig:
    """Immutable configuration for Google Ads API authentication."""

    developer_token: str
    client_id: str
    client_secret: str
    refresh_token: str
    login_customer_id: str | None = None


def load_config_from_env() -> GoogleAdsConfig:
    """Load Google Ads configuration from environment variables.

    Returns:
        GoogleAdsConfig with all credentials.

    Raises:
        AuthenticationError: If required env vars are missing.
    """
    values: dict[str, Any] = {}
    missing: list[str] = []

    for env_var, field_name in _REQUIRED_ENV_VARS.items():
        val = os.environ.get(env_var)
        if not val:
            missing.append(env_var)
        else:
            values[field_name] = val

    if missing:
        raise AuthenticationError(
            f"Variabili ambiente mancanti: {', '.join(missing)}. "
            "Imposta le credenziali in .env o nelle variabili ambiente.",
        )

    for env_var, field_name in _OPTIONAL_ENV_VARS.items():
        val = os.environ.get(env_var)
        if val:
            values[field_name] = val

    return GoogleAdsConfig(**values)


def create_google_ads_client(config: GoogleAdsConfig) -> GoogleAdsClient:
    """Create a GoogleAdsClient from config.

    Args:
        config: Authentication configuration.

    Returns:
        Initialized GoogleAdsClient.

    Raises:
        AuthenticationError: If client creation fails.
    """
    client_config: dict[str, Any] = {
        "developer_token": config.developer_token,
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "refresh_token": config.refresh_token,
        "use_proto_plus": True,
    }
    if config.login_customer_id:
        client_config["login_customer_id"] = config.login_customer_id

    try:
        return GoogleAdsClient.load_from_dict(client_config)
    except Exception as exc:
        raise AuthenticationError(
            f"Impossibile creare Google Ads client: {exc}"
        ) from exc
