"""Customer match list mutation tools for Google Ads MCP server."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.common import sanitize_customer_id
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client


def _hash_value(value: str) -> str:
    """SHA256-hash a normalized value for Customer Match upload.

    Args:
        value: Raw value (email, phone, etc.).

    Returns:
        Lowercase hex SHA256 digest.
    """
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _build_user_data_list(
    client: Any,
    emails: str,
    phones: str,
) -> list[Any]:
    """Build a list of UserData objects from email and phone inputs.

    Emails are lowercased and SHA256-hashed. Phone numbers are stripped
    and SHA256-hashed.

    Args:
        client: GoogleAdsClientWrapper instance.
        emails: Comma-separated email addresses.
        phones: Comma-separated phone numbers.

    Returns:
        List of UserData proto objects.
    """
    user_data_list: list[Any] = []

    if emails:
        for email in emails.split(","):
            email = email.strip().lower()
            if email:
                user_data = client.client.get_type("UserData")
                user_identifier = client.client.get_type("UserIdentifier")
                user_identifier.hashed_email = _hash_value(email)
                user_data.user_identifiers.append(user_identifier)
                user_data_list.append(user_data)

    if phones:
        for phone in phones.split(","):
            phone = phone.strip()
            if phone:
                user_data = client.client.get_type("UserData")
                user_identifier = client.client.get_type("UserIdentifier")
                user_identifier.hashed_phone_number = _hash_value(phone)
                user_data.user_identifiers.append(user_identifier)
                user_data_list.append(user_data)

    return user_data_list


@mcp.tool()
def gads_upload_customer_list(
    customer_id: str,
    user_list_id: str,
    emails: str = "",
    phones: str = "",
    ctx: Context = None,
) -> str:
    """Upload members to a customer match list.

    Email addresses and phone numbers are automatically SHA256-hashed
    before upload, as required by the Google Ads API.

    Args:
        customer_id: Google Ads customer ID.
        user_list_id: The user list resource ID.
        emails: Comma-separated email addresses (will be SHA256 hashed).
        phones: Comma-separated phone numbers (will be SHA256 hashed).
    """
    cid = sanitize_customer_id(customer_id)
    client = get_client(ctx)

    user_data_list = _build_user_data_list(client, emails, phones)

    if not user_data_list:
        return json.dumps(
            {"error": "No valid emails or phones provided."},
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    service = client.get_service("UserDataService")

    request = client.client.get_type("UploadUserDataRequest")
    request.customer_id = cid

    for ud in user_data_list:
        op = client.client.get_type("UserDataOperation")
        op.create = ud
        request.operations.append(op)

    customer_match_metadata = client.client.get_type(
        "CustomerMatchUserListMetadata"
    )
    customer_match_metadata.user_list = (
        f"customers/{cid}/userLists/{user_list_id}"
    )
    request.customer_match_user_list_metadata = customer_match_metadata

    response = service.upload_user_data(request=request)

    received_count = (
        response.received_operations_count
        if hasattr(response, "received_operations_count")
        else len(user_data_list)
    )

    return json.dumps(
        {
            "uploaded": len(user_data_list),
            "received_operations_count": received_count,
        },
        indent=2,
        ensure_ascii=False,
        default=str,
    )


@mcp.tool()
def gads_remove_customer_list_members(
    customer_id: str,
    user_list_id: str,
    emails: str = "",
    phones: str = "",
    ctx: Context = None,
) -> str:
    """Remove members from a customer match list.

    Email addresses and phone numbers are automatically SHA256-hashed
    before the removal request, as required by the Google Ads API.

    Args:
        customer_id: Google Ads customer ID.
        user_list_id: The user list resource ID.
        emails: Comma-separated email addresses to remove (will be SHA256 hashed).
        phones: Comma-separated phone numbers to remove (will be SHA256 hashed).
    """
    cid = sanitize_customer_id(customer_id)
    client = get_client(ctx)

    user_data_list = _build_user_data_list(client, emails, phones)

    if not user_data_list:
        return json.dumps(
            {"error": "No valid emails or phones provided."},
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    service = client.get_service("UserDataService")

    request = client.client.get_type("UploadUserDataRequest")
    request.customer_id = cid

    for ud in user_data_list:
        op = client.client.get_type("UserDataOperation")
        op.remove = ud
        request.operations.append(op)

    customer_match_metadata = client.client.get_type(
        "CustomerMatchUserListMetadata"
    )
    customer_match_metadata.user_list = (
        f"customers/{cid}/userLists/{user_list_id}"
    )
    request.customer_match_user_list_metadata = customer_match_metadata

    response = service.upload_user_data(request=request)

    received_count = (
        response.received_operations_count
        if hasattr(response, "received_operations_count")
        else len(user_data_list)
    )

    return json.dumps(
        {
            "removed": len(user_data_list),
            "received_operations_count": received_count,
        },
        indent=2,
        ensure_ascii=False,
        default=str,
    )
