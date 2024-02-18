import logging
from functools import lru_cache
from typing import Tuple, Iterable

from fetchfox import rest
from fetchfox.checks import check_str
from fetchfox.constants.blockchains import ETHEREUM, POLYGON

BASE_URL = "https://api.opensea.io"

BLOCKCHAINS = {
    ETHEREUM: "ethereum",
    POLYGON: "matic",
}

logger = logging.getLogger(__name__)


def get(service: str, api_key: str, params: dict = None, version: int = 2, check: str = None) -> Tuple[dict, int]:
    check_str(api_key, "openseaio.api_key")

    if version == 1:
        url = f"{BASE_URL}/api/v{version}/{service}"
    else:
        url = f"{BASE_URL}/v{version}/{service}"

    return rest.get(
        url=url,
        headers={
            "X-API-KEY": api_key,
        },
        params=params,
        sleep=2.5,
        check=check,
    )


@lru_cache(maxsize=None)
def get_collection_slug(contract_address: str, blockchain: str, api_key: str) -> str:
    check_str(contract_address, "openseaio.contract_address")
    check_str(blockchain, "openseaio.blockchain")

    contract_address = contract_address.strip().lower()
    blockchain: str = BLOCKCHAINS.get(blockchain, blockchain)

    logger.info("fetching slug for %s (%s)", contract_address, blockchain)

    response, status_code = get(
        f"chain/{blockchain}/contract/{contract_address}",
        api_key=api_key,
        check="collection",
    )

    return response["collection"]


def get_collection_sales(contract_address: str, blockchain: str, api_key: str, slug: str = None) -> Iterable[dict]:
    check_str(contract_address, "openseaio.contract_address")
    check_str(blockchain, "openseaio.blockchain")

    contract_address = contract_address.strip().lower()

    if not slug:
        slug = get_collection_slug(contract_address, blockchain, api_key=api_key)

    cursor = ""

    while True:
        response, status_code = get(
            f"events/collection/{slug}",
            params={
                "event_type": "sale",
                "next": cursor,
            },
            api_key=api_key,
        )

        for event in response["asset_events"]:
            if event["event_type"] != "sale":
                continue

            yield event

        cursor = response.get("next")

        if not cursor:
            break


def get_collection_listings(contract_address: str, blockchain: str, api_key: str, slug: str = None) -> Iterable[dict]:
    check_str(contract_address, "openseaio.contract_address")
    check_str(blockchain, "openseaio.blockchain")

    contract_address = contract_address.strip().lower()

    if not slug:
        slug = get_collection_slug(contract_address, blockchain, api_key=api_key)

    cursor = ""

    while True:
        response, status_code = get(
            f"listings/collection/{slug}/all",
            params={
                "next": cursor,
            },
            api_key=api_key,
        )

        yield from response.get("listings", [])

        cursor = response.get("next")

        if not cursor:
            break
