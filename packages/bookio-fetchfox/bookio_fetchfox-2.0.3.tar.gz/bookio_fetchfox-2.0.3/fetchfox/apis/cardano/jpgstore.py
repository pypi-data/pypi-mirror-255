import logging
from typing import Iterable, Tuple

from fetchfox import rest
from fetchfox.checks import check_str

BASE_URL = "https://server.jpgstoreapis.com"

logger = logging.getLogger(__name__)


def get(service: str, params: dict = None, headers: dict = None) -> Tuple[dict, int]:
    return rest.get(
        url=f"{BASE_URL}/{service}",
        params=params,
        headers=headers,
        sleep=0.5,
    )


def get_collection_listings(policy_id: str) -> Iterable[dict]:
    check_str(policy_id, "jpgstore.policy_id")
    policy_id = policy_id.strip().lower()

    cursor = ""

    while True:
        params = {}

        if cursor:
            params["cursor"] = cursor

        response, status_code = get(
            f"policy/{policy_id}/listings",
            params=params,
        )

        cursor = response.get("nextPageCursor")

        if not cursor:  # pragma: no cover
            break

        yield from response["listings"]


def get_collection_sales(policy_id: str) -> Iterable[dict]:
    check_str(policy_id, "jpgstore.policy_id")
    policy_id = policy_id.strip().lower()

    txs = set()

    last_date = ""

    while True:
        response, status_code = get(
            f"collection/{policy_id}/v2/transactions",
            params={
                "lastDate": last_date,
                "count": 50,
            },
            headers={
                "x-jpgstore-csrf-protection": "1",
            },
        )

        transactions = response["transactions"]

        if not transactions:  # pragma: no cover
            break

        for sale in transactions:
            tx_hash = sale["tx_hash"]

            if tx_hash in txs:
                continue

            txs.add(tx_hash)
            last_date = sale["created_at"]

            yield sale
