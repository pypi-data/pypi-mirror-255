from typing import Tuple, Dict

from stigg.generated import FetchEntitlementsQuery, GetPaywallInput, FetchEntitlementQuery


def build_get_entitlement_data(edge_url: str, query: FetchEntitlementQuery) -> Tuple[str, Dict]:
  url = f"{edge_url}/v1/c/{query.customer_id}/entitlements.json"
  params = {}
  if query.resource_id is not None:
    params["resourceId"] = query.resource_id

  if query.feature_id is not None:
    params["featureId"] = query.feature_id

  if query.options is not None and query.options.requested_usage is not None:
    params['requestedUsage'] = query.options.requested_usage

  return url, params


def build_get_entitlements_data(edge_url: str, query: FetchEntitlementsQuery) -> Tuple[str, Dict]:
    url = f"{edge_url}/v1/c/{query.customer_id}/entitlements.json"
    params = {}
    if query.resource_id is not None:
        params["resourceId"] = query.resource_id

    return url, params


def build_get_paywall_data(edge_url: str, _input: GetPaywallInput) -> Tuple[str, Dict]:
    if _input.product_id is not None:
        url = f"{edge_url}/v1/p/{_input.product_id}/paywall.json"
    else:
        url = f"{edge_url}/v1/paywall.json"

    params = {}
    if _input.billing_country_code is not None:
        params["billingCountryCode"] = _input.billing_country_code

    if _input.fetch_all_countries_prices is not None:
        params["fetchAllCountriesPrices"] = _input.fetch_all_countries_prices

    return url, params
