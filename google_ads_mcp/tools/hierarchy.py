"""Account hierarchy tools for Google Ads MCP server."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context

from google_ads_mcp.models.common import sanitize_customer_id
from google_ads_mcp.server import mcp
from google_ads_mcp.tools._helpers import get_client, safe_int, safe_str
from google_ads_mcp.utils.formatting import format_table_markdown
from google_ads_mcp.utils.pagination import paginate_results


# ---------------------------------------------------------------------------
# 1. gads_list_customer_clients
# ---------------------------------------------------------------------------

def _build_customer_clients_query() -> str:
    """Build GAQL query for listing client accounts under a manager."""
    return (
        "SELECT customer_client.client_customer, "
        "customer_client.descriptive_name, "
        "customer_client.level, "
        "customer_client.manager, "
        "customer_client.status, "
        "customer_client.currency_code, "
        "customer_client.time_zone "
        "FROM customer_client"
    )


def _parse_customer_client_row(row: Any) -> dict[str, Any]:
    """Extract customer client fields from a GAQL result row."""
    cc = row.customer_client
    return {
        "client_customer": safe_str(cc.client_customer),
        "descriptive_name": safe_str(cc.descriptive_name),
        "level": safe_str(cc.level),
        "manager": safe_str(cc.manager),
        "status": safe_str(cc.status).replace("CustomerStatus.", ""),
        "currency_code": safe_str(cc.currency_code),
        "time_zone": safe_str(cc.time_zone),
    }


@mcp.tool()
def gads_list_customer_clients(
    customer_id: str,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List client accounts under a manager (MCC) account.

    Args:
        customer_id: Google Ads manager (MCC) customer ID (e.g. '1234567890' or '123-456-7890').
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    clean_id = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_customer_clients_query()
    rows = client.query(clean_id, query)

    clients = [_parse_customer_client_row(row) for row in rows]
    page, pagination = paginate_results(clients, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"customer_clients": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = [
        "client_customer", "descriptive_name", "level",
        "manager", "status", "currency_code", "time_zone",
    ]
    headers = {
        "client_customer": "Client",
        "descriptive_name": "Name",
        "level": "Level",
        "manager": "Manager",
        "status": "Status",
        "currency_code": "Currency",
        "time_zone": "Time Zone",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Customer Clients ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} client accounts"
        f"{' (more available)' if info['has_more'] else ''}_"
    )


# ---------------------------------------------------------------------------
# 2. gads_list_accessible_customers
# ---------------------------------------------------------------------------

@mcp.tool()
def gads_list_accessible_customers(
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List all customer accounts accessible with current credentials.

    This tool does not require a customer_id because it uses the
    CustomerService.list_accessible_customers() API.

    Args:
        response_format: Output format: markdown or json.
    """
    client = get_client(ctx)
    service = client.get_service("CustomerService")
    response = service.list_accessible_customers()
    resource_names = list(response.resource_names)

    # Extract customer IDs from resource names (format: "customers/1234567890")
    customers = []
    for rn in resource_names:
        cid = rn.split("/")[-1] if "/" in rn else rn
        customers.append({"resource_name": rn, "customer_id": cid})

    if response_format == "json":
        return json.dumps(
            {"accessible_customers": customers, "total": len(customers)},
            indent=2,
            ensure_ascii=False,
        )

    if not customers:
        return "## Accessible Customers\n\n_No accessible customer accounts found._"

    lines = [
        f"## Accessible Customers ({len(customers)})\n",
    ]
    for c in customers:
        lines.append(f"- **{c['customer_id']}** (`{c['resource_name']}`)")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 3. gads_list_merchant_center_links
# ---------------------------------------------------------------------------

def _build_merchant_center_links_query() -> str:
    """Build GAQL query for listing Merchant Center links."""
    return (
        "SELECT merchant_center_link.id, "
        "merchant_center_link.merchant_center_account_name, "
        "merchant_center_link.status "
        "FROM merchant_center_link"
    )


def _parse_merchant_center_link_row(row: Any) -> dict[str, Any]:
    """Extract Merchant Center link fields from a GAQL result row."""
    mcl = row.merchant_center_link
    return {
        "merchant_id": safe_str(mcl.id),
        "account_name": safe_str(mcl.merchant_center_account_name),
        "status": safe_str(mcl.status).replace("MerchantCenterLinkStatus.", ""),
    }


@mcp.tool()
def gads_list_merchant_center_links(
    customer_id: str,
    limit: int = 50,
    offset: int = 0,
    response_format: str = "markdown",
    ctx: Context = None,
) -> str:
    """List Merchant Center accounts linked to the Google Ads account.

    Args:
        customer_id: Google Ads customer ID (e.g. '1234567890' or '123-456-7890').
        limit: Max results (1-1000, default 50).
        offset: Starting offset for pagination.
        response_format: Output format: markdown or json.
    """
    clean_id = sanitize_customer_id(customer_id)
    client = get_client(ctx)
    query = _build_merchant_center_links_query()
    rows = client.query(clean_id, query)

    links = [_parse_merchant_center_link_row(row) for row in rows]
    page, pagination = paginate_results(links, limit, offset)

    if response_format == "json":
        return json.dumps(
            {"merchant_center_links": page, "pagination": pagination.to_dict()},
            indent=2,
            ensure_ascii=False,
        )

    columns = ["merchant_id", "account_name", "status"]
    headers = {
        "merchant_id": "Merchant ID",
        "account_name": "Account Name",
        "status": "Status",
    }
    table = format_table_markdown(page, columns, headers)
    info = pagination.to_dict()
    return (
        f"## Merchant Center Links ({info['count']}/{info['total']})\n\n"
        f"{table}\n\n"
        f"_Showing {info['count']} of {info['total']} linked accounts"
        f"{' (more available)' if info['has_more'] else ''}_"
    )
