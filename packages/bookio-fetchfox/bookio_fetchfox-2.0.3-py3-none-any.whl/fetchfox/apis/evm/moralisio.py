import logging
from functools import lru_cache
from typing import Iterable, Tuple

from fetchfox import rest
from fetchfox.checks import check_str

BASE_URL = "https://deep-index.moralis.io/api"

logger = logging.getLogger(__name__)


def get(service: str, blockchain: str, api_key: str, params: dict = None, version: int = 2) -> Tuple[dict, int]:
    check_str(blockchain, "moralisio.blockchain")
    check_str(api_key, "moralisio.api_key")

    params = params or {}
    params["chain"] = "eth" if blockchain == "ethereum" else blockchain

    return rest.get(
        url=f"{BASE_URL}/v{version}/{service}",
        params=params,
        headers={
            "X-API-Key": api_key,
            "Host": "deep-index.moralis.io",
        },
    )


def get_account_balance(address: str, blockchain: str, api_key: str) -> Iterable[dict]:
    check_str(address, "moralisio.address")
    address = address.strip().lower()

    response, status_code = get(
        f"{address}/balance",
        blockchain=blockchain,
        api_key=api_key,
    )

    return int(response["balance"]) / 10**18


def get_account_assets(address: str, blockchain: str, api_key: str) -> Iterable[dict]:
    check_str(address, "moralisio.address")
    address = address.strip().lower()

    cursor = ""

    while True:
        response, status_code = get(
            f"{address}/nft",
            params={
                "cursor": cursor,
            },
            blockchain=blockchain,
            api_key=api_key,
        )

        yield from response.get("result", [])

        if not response.get("cursor"):
            break

        cursor = response["cursor"]


@lru_cache(maxsize=None)
def get_asset_data(contract_address: str, asset_id: str, blockchain: str, api_key: str) -> dict:
    check_str(contract_address, "moralisio.contract_address")
    check_str(asset_id, "moralisio.asset_id")
    contract_address = contract_address.strip().lower()

    response, status_code = get(
        f"nft/{contract_address}/{asset_id}",
        blockchain=blockchain,
        api_key=api_key,
    )

    if status_code == 404:
        raise Exception(f"{contract_address}/{asset_id} doesn't exist")

    if not response.get("metadata"):
        resync_asset_metadata(
            contract_address,
            asset_id,
            blockchain,
            api_key=api_key,
        )

        return get_asset_data(contract_address, asset_id, blockchain, api_key=api_key)

    return response


def resync_asset_metadata(contract_address: str, asset_id: str, blockchain: str, api_key: str):
    check_str(contract_address, "moralisio.contract_address")
    check_str(asset_id, "moralisio.asset_id")
    contract_address = contract_address.strip().lower()

    response, status_code = get(
        f"nft/{contract_address}/{asset_id}/metadata/resync",
        params={
            "flag": "uri",
            "mode": "sync",
        },
        blockchain=blockchain,
        api_key=api_key,
    )

    if status_code == 404:
        raise ValueError(f"{contract_address}/{asset_id} doesn't exist")

    return response.get("status")


def get_asset_owner(contract_address: str, asset_id: str, blockchain: str, api_key: str) -> dict:
    check_str(contract_address, "moralisio.contract_address")
    check_str(asset_id, "moralisio.asset_id")
    contract_address = contract_address.strip().lower()

    response, status_code = get(
        f"nft/{contract_address}/{asset_id}/owners",
        blockchain=blockchain,
        api_key=api_key,
    )

    for holding in response["result"]:
        return {
            "contract_address": holding["token_address"],
            "asset_id": holding["token_id"],
            "address": holding["owner_of"],
            "amount": holding["amount"],
        }


def get_collection_assets(contract_address: str, blockchain: str, api_key: str) -> Iterable[dict]:
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    cursor = ""

    while True:
        response, status_code = get(
            f"nft/{contract_address}",
            params={
                "cursor": cursor,
                "format": "decimal",
                "normalizeMetadata": "false",
            },
            blockchain=blockchain,
            api_key=api_key,
        )

        for item in response.get("result", []):
            yield item["token_id"]

        if not response.get("cursor"):
            break

        cursor = response["cursor"]


def get_collection_owners(contract_address: str, blockchain: str, api_key: str) -> Iterable[dict]:
    check_str(contract_address, "moralisio.contract_address")
    contract_address = contract_address.strip().lower()

    cursor = ""

    while True:
        response, status_code = get(
            f"nft/{contract_address}/owners",
            params={
                "cursor": cursor,
            },
            blockchain=blockchain,
            api_key=api_key,
        )

        for holding in response["result"]:
            yield {
                "contract_address": holding["token_address"],
                "asset_id": holding["token_id"],
                "address": holding["owner_of"],
                "amount": holding["amount"],
            }

        cursor = response.get("cursor")

        if not cursor:
            break
