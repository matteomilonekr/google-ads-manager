"""Google Ads API client wrapper with retry logic."""

from __future__ import annotations

import time
import logging
from typing import Any

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core.exceptions import InternalServerError, ServiceUnavailable

from google_ads_mcp.utils.errors import (
    GoogleAdsMCPError,
    AuthenticationError,
    QuotaExhaustedError,
    ResourceNotFoundError,
    format_google_ads_error,
)

logger = logging.getLogger(__name__)

_TRANSIENT_ERRORS = (InternalServerError, ServiceUnavailable, ConnectionError)


class GoogleAdsClientWrapper:
    """Wrapper around GoogleAdsClient providing query, mutate, and retry logic."""

    def __init__(
        self,
        client: GoogleAdsClient,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ) -> None:
        self.client = client
        self.max_retries = max_retries
        self.base_delay = base_delay

    def get_service(self, service_name: str) -> Any:
        """Get a Google Ads API service by name."""
        return self.client.get_service(service_name)

    def query(
        self,
        customer_id: str,
        query: str,
        page_size: int = 10000,
    ) -> list[Any]:
        """Execute a GAQL SELECT query with retry.

        Args:
            customer_id: Google Ads customer ID (10 digits, no dashes).
            query: GAQL query string (SELECT only).
            page_size: Results per page.

        Returns:
            List of result rows.

        Raises:
            ValueError: If query is not a SELECT.
            GoogleAdsMCPError: On API errors.
        """
        stripped = query.strip()
        if not stripped.upper().startswith("SELECT"):
            raise ValueError(
                f"Solo query SELECT consentite. Ricevuto: '{stripped[:30]}...'"
            )

        return self._execute_with_retry(
            self._do_query, customer_id, stripped, page_size
        )

    def mutate(
        self,
        customer_id: str,
        operations: list[Any],
        partial_failure: bool = False,
    ) -> Any:
        """Execute mutate operations with retry.

        Args:
            customer_id: Google Ads customer ID.
            operations: List of mutate operations.
            partial_failure: Allow partial failures.

        Returns:
            Mutate response.
        """
        return self._execute_with_retry(
            self._do_mutate, customer_id, operations, partial_failure
        )

    def _do_query(
        self, customer_id: str, query: str, page_size: int
    ) -> list[Any]:
        service = self.get_service("GoogleAdsService")
        request = self.client.get_type("SearchGoogleAdsRequest")
        request.customer_id = customer_id
        request.query = query
        request.page_size = page_size
        response = service.search(request=request)
        return list(response)

    def _do_mutate(
        self,
        customer_id: str,
        operations: list[Any],
        partial_failure: bool,
    ) -> Any:
        service = self.get_service("GoogleAdsService")
        return service.mutate(
            customer_id=customer_id,
            mutate_operations=operations,
            partial_failure=partial_failure,
        )

    def _execute_with_retry(self, func: Any, *args: Any) -> Any:
        """Execute a function with exponential backoff retry on transient errors."""
        last_exception: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args)
            except GoogleAdsException as exc:
                self._handle_google_ads_exception(exc)
            except _TRANSIENT_ERRORS as exc:
                last_exception = exc
                if attempt < self.max_retries:
                    delay = self.base_delay * (2**attempt)
                    logger.warning(
                        "Transient error (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1,
                        self.max_retries + 1,
                        delay,
                        exc,
                    )
                    time.sleep(delay)
                else:
                    raise GoogleAdsMCPError(
                        f"Errore dopo {self.max_retries + 1} tentativi: {exc}"
                    ) from exc

        raise GoogleAdsMCPError(
            f"Errore inaspettato dopo retry: {last_exception}"
        )

    def _handle_google_ads_exception(self, exc: GoogleAdsException) -> None:
        """Convert GoogleAdsException to appropriate MCP error."""
        for error in exc.failure.errors:
            error_code = error.error_code
            message = error.message

            code_name = str(error_code).split(".")[-1] if error_code else "UNKNOWN"

            if "authentication" in code_name.lower() or "authorization" in code_name.lower():
                raise AuthenticationError(
                    format_google_ads_error("AUTHENTICATION_ERROR", message)
                ) from exc
            if "quota" in code_name.lower() or "rate" in code_name.lower():
                raise QuotaExhaustedError(
                    format_google_ads_error("QUOTA_ERROR", message),
                    retry_after_seconds=60,
                ) from exc
            if "not_found" in code_name.lower():
                raise ResourceNotFoundError(
                    format_google_ads_error("RESOURCE_NOT_FOUND", message),
                ) from exc

        raise GoogleAdsMCPError(
            format_google_ads_error("REQUEST_ERROR", str(exc))
        ) from exc
