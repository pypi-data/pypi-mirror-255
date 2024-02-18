import json
from base64 import b64decode
from functools import lru_cache
from typing import Iterable, Tuple

from fetchfox import rest
from fetchfox.checks import check_str

BASE_URL = "https://mainnet-idx.algonode.cloud"


def get(service: str, params: dict = None, version: int = 2) -> Tuple[dict, int]:
    return rest.get(
        url=f"{BASE_URL}/v{version}/{service}",
        params=params,
    )


def get_account_assets(address: str) -> Iterable[dict]:
    check_str(address, "algonodecloud.address")
    address = address.strip().upper()

    response, status_code = get(f"accounts/{address}")

    account = response["account"]

    for asset in account.get("assets", []):
        yield asset


def get_account_balance(address: str) -> Iterable[str]:
    check_str(address, "algonodecloud.address")
    address = address.strip().upper()

    response, status_code = get(f"accounts/{address}")

    return int(response["account"]["amount"]) / 10**6


@lru_cache(maxsize=None)
def get_asset_data(asset_id: str) -> dict:
    check_str(asset_id, "algonodecloud.asset_id")

    response, status_code = get(f"assets/{asset_id}")

    return response["asset"]["params"]


@lru_cache(maxsize=None)
def get_asset_metadata(asset_id: str) -> dict:
    check_str(asset_id, "algonodecloud.asset_id")

    response, status_code = get(
        f"assets/{asset_id}/transactions",
        params={
            "tx-type": "acfg",
            "limit": "1",
        },
    )

    transaction = response["transactions"][0]
    note = b64decode(transaction["note"]).decode("utf-8")

    return json.loads(note)


def get_asset_owner(asset_id: str) -> dict:
    check_str(asset_id, "algonodecloud.asset_id")

    response, status_code = get(
        f"assets/{asset_id}/balances",
        params={
            "currency-greater-than": "0",
        },
    )

    balances = response.get("balances", [])

    if not balances:
        return None

    return {
        "asset_id": asset_id,
        "address": balances[0]["address"],
        "amount": balances[0]["amount"],
    }


def get_collection_assets(creator_address: str) -> Iterable[str]:
    check_str(creator_address, "algonodecloud.creator_address")
    creator_address = creator_address.strip().upper()

    response, status_code = get(f"accounts/{creator_address}")

    assets = sorted(
        response["account"].get("created-assets", []),
        key=lambda a: a["index"],
        reverse=True,
    )

    for asset in assets:
        yield asset["index"]
