from cachetools.func import ttl_cache

from fetchfox import rest
from fetchfox.checks import check_str

BASE_URL = "https://api.muesliswap.com"


@ttl_cache(ttl=60)
def get_asset_price(asset_id: str) -> float:
    check_str(asset_id, "muesliswap.asset_id")

    policy_id, asset_name = asset_id[:56], asset_id[56:]

    response, status_code = rest.get(
        url=f"{BASE_URL}/price",
        params={
            "quote-policy-id": policy_id,
            "quote-tokenname": asset_name,
        },
    )

    return response["price"]
