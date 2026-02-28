"""Centralized error handling for Google Ads MCP server."""

from __future__ import annotations

from typing import Any


class GoogleAdsMCPError(Exception):
    """Base exception for all Google Ads MCP errors."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationError(GoogleAdsMCPError):
    """Raised when Google Ads authentication fails."""


class QuotaExhaustedError(GoogleAdsMCPError):
    """Raised when API quota is exhausted."""

    def __init__(
        self,
        message: str,
        *,
        retry_after_seconds: int = 0,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details=details)
        self.retry_after_seconds = retry_after_seconds


class ResourceNotFoundError(GoogleAdsMCPError):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        message: str,
        *,
        resource_type: str = "",
        resource_id: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details=details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class InvalidInputError(GoogleAdsMCPError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        *,
        field: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details=details)
        self.field = field


_ERROR_MESSAGES: dict[str, str] = {
    "AUTHENTICATION_ERROR": (
        "Errore auth: verifica developer_token e refresh_token. "
        "Rigenera token se scaduto."
    ),
    "QUOTA_ERROR": (
        "Quota esaurita: attendi prima di riprovare. "
        "Limite: controlla developer token access level."
    ),
    "REQUEST_ERROR": "Errore nella request: verifica customer_id e parametri.",
    "INTERNAL_ERROR": (
        "Errore interno Google Ads: riprova tra 30s. "
        "Se persiste, controlla status.cloud.google.com"
    ),
    "RESOURCE_NOT_FOUND": "Risorsa non trovata: verifica che l'ID sia corretto e accessibile.",
    "FIELD_ERROR": "Campo non valido nella query GAQL. Controlla sintassi e nomi campi.",
}


def format_google_ads_error(error_code: str, error_detail: str) -> str:
    """Format a Google Ads API error into a user-friendly message.

    Args:
        error_code: The error code string (e.g. 'AUTHENTICATION_ERROR').
        error_detail: Additional detail from the API.

    Returns:
        Human-readable error message.
    """
    base_message = _ERROR_MESSAGES.get(error_code, f"Errore Google Ads ({error_code})")
    return f"{base_message} Dettaglio: {error_detail}"
