"""Tests for Google Ads authentication module."""

import os
import pytest
from unittest.mock import patch, MagicMock
from google_ads_mcp.auth import (
    GoogleAdsConfig,
    load_config_from_env,
    create_google_ads_client,
)
from google_ads_mcp.utils.errors import AuthenticationError


class TestGoogleAdsConfig:
    def test_all_fields_required(self):
        config = GoogleAdsConfig(
            developer_token="dev123",
            client_id="client123",
            client_secret="secret123",
            refresh_token="refresh123",
        )
        assert config.developer_token == "dev123"
        assert config.login_customer_id is None

    def test_with_login_customer_id(self):
        config = GoogleAdsConfig(
            developer_token="dev123",
            client_id="client123",
            client_secret="secret123",
            refresh_token="refresh123",
            login_customer_id="1234567890",
        )
        assert config.login_customer_id == "1234567890"


class TestLoadConfigFromEnv:
    def test_loads_all_env_vars(self):
        env = {
            "GOOGLE_ADS_DEVELOPER_TOKEN": "dev_tok",
            "GOOGLE_ADS_CLIENT_ID": "cli_id",
            "GOOGLE_ADS_CLIENT_SECRET": "cli_sec",
            "GOOGLE_ADS_REFRESH_TOKEN": "ref_tok",
            "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "1234567890",
        }
        with patch.dict(os.environ, env, clear=False):
            config = load_config_from_env()
        assert config.developer_token == "dev_tok"
        assert config.client_id == "cli_id"
        assert config.login_customer_id == "1234567890"

    def test_missing_required_raises(self):
        env = {"GOOGLE_ADS_DEVELOPER_TOKEN": "tok"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(AuthenticationError, match="CLIENT_ID"):
                load_config_from_env()

    def test_login_customer_id_optional(self):
        env = {
            "GOOGLE_ADS_DEVELOPER_TOKEN": "dev_tok",
            "GOOGLE_ADS_CLIENT_ID": "cli_id",
            "GOOGLE_ADS_CLIENT_SECRET": "cli_sec",
            "GOOGLE_ADS_REFRESH_TOKEN": "ref_tok",
        }
        with patch.dict(os.environ, env, clear=True):
            config = load_config_from_env()
        assert config.login_customer_id is None


class TestCreateGoogleAdsClient:
    @patch("google_ads_mcp.auth.GoogleAdsClient")
    def test_creates_client_with_config(self, mock_client_cls):
        config = GoogleAdsConfig(
            developer_token="dev",
            client_id="cid",
            client_secret="csec",
            refresh_token="rtok",
        )
        mock_client_cls.load_from_dict.return_value = MagicMock()
        client = create_google_ads_client(config)
        mock_client_cls.load_from_dict.assert_called_once()
        assert client is not None

    @patch("google_ads_mcp.auth.GoogleAdsClient")
    def test_includes_login_customer_id_when_set(self, mock_client_cls):
        config = GoogleAdsConfig(
            developer_token="dev",
            client_id="cid",
            client_secret="csec",
            refresh_token="rtok",
            login_customer_id="1234567890",
        )
        mock_client_cls.load_from_dict.return_value = MagicMock()
        create_google_ads_client(config)
        call_args = mock_client_cls.load_from_dict.call_args[0][0]
        assert call_args["login_customer_id"] == "1234567890"

    @patch("google_ads_mcp.auth.GoogleAdsClient")
    def test_wraps_sdk_errors(self, mock_client_cls):
        config = GoogleAdsConfig(
            developer_token="dev",
            client_id="cid",
            client_secret="csec",
            refresh_token="rtok",
        )
        mock_client_cls.load_from_dict.side_effect = Exception("SDK error")
        with pytest.raises(AuthenticationError, match="SDK error"):
            create_google_ads_client(config)
