import logging
from functools import lru_cache
from typing import Iterable, Tuple

from fetchfox import rest
from fetchfox.checks import check_str

BASE_URL = "https://api.nftexplorer.app"

logger = logging.getLogger(__name__)


def get(service: str, api_key: str, params: dict = None, version: int = 1) -> Tuple[dict, int]:
    check_str(api_key, "nftexplorerapp.api_key")

    return rest.get(
        url=f"{BASE_URL}/v{version}/{service}",
        headers={
            "Authorization": api_key,
        },
        params=params,
        sleep=1,
    )


@lru_cache(maxsize=None)
def get_collection_id(creator_address: str, api_key: str) -> str:
    check_str(creator_address, "randswap.creator_address")
    creator_address = creator_address.strip().upper()

    response, status_code = get(
        "collections/search",
        params={
            "q": creator_address,
        },
        api_key=api_key,
    )

    if response.get("error"):
        logger.error("error fetching sales on algorand: %s", response["error"])
        return

    verified = response["results"].get("verified", [])

    if verified:
        return verified[0]["collectionId"]

    recognized = response["results"].get("recognized", [])

    if recognized:
        return recognized[0]["collectionId"]

    return None


def get_collection_sales(creator_address: str, api_key: str) -> Iterable[dict]:
    check_str(creator_address, "randswap.creator_address")
    creator_address = creator_address.strip().upper()

    collection_id = get_collection_id(creator_address, api_key)

    if not collection_id:
        return

    next_token = ""

    while True:
        response, status_code = get(
            "/collections/salesHistory",
            params={
                "collectionId": collection_id,
                "nextToken": next_token,
            },
            api_key=api_key,
        )

        if response.get("error"):
            logger.error("error fetching sales on algorand: %s", response["error"])
            return

        yield from response["sales"]

        next_token = response.get("nextToken")

        if not next_token:
            break
