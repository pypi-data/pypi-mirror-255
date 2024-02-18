import base64
from functools import lru_cache
from typing import Iterable, Tuple

from fetchfox import rest
from fetchfox.checks import check_str
from fetchfox.constants.cardano import ADA_HANDLE_POLICY_ID

BASE_URL = "https://mainnet.gomaestro-api.org"


def get(service: str, api_key: str, params: dict = None, version: int = 1) -> Tuple[dict, int]:
    check_str(api_key, "gomaestro.api_key")

    return rest.get(
        url=f"{BASE_URL}/v{version}/{service}",
        params=params,
        headers={
            "api-key": api_key,
        },
    )


def get_account_assets(stake_address: str, api_key: str, policy_id: str = None) -> Iterable[Tuple[str, int]]:
    check_str(stake_address, "gomaestro.stake_address")
    stake_address = stake_address.strip().lower()

    if policy_id:
        policy_id = policy_id.strip().lower()

    cursor = None

    while True:
        response, status_code = get(
            f"accounts/{stake_address}/assets",
            params={
                "cursor": cursor,
                "policy": policy_id,
            },
            api_key=api_key,
        )

        yield from response.get("data", [])

        cursor = response.get("next_cursor")

        if not cursor:
            break


def get_account_balance(stake_address: str, api_key: str) -> float:
    check_str(stake_address, "gomaestro.stake_address")

    response, status_code = get(
        f"accounts/{stake_address}",
        api_key=api_key,
    )

    return response["data"]["total_balance"] / 10**6


def get_collection_owners(policy_id: str, api_key: str) -> Iterable[dict]:
    check_str(api_key, "gomaestro.api-key")
    policy_id = policy_id.strip().lower()

    cursor = None

    while True:
        response, status_code = get(
            f"policy/{policy_id}/accounts",
            params={
                "cursor": cursor,
            },
            api_key=api_key,
        )

        yield from response.get("data", [])

        cursor = response.get("next_cursor")

        if not cursor:
            break


def get_asset_owners(asset_id: str, api_key: str) -> dict:
    check_str(asset_id, "gomaestro.asset_id")

    cursor = None

    while True:
        response, status_code = get(
            f"assets/{asset_id}/accounts",
            params={
                "cursor": cursor,
            },
            api_key=api_key,
        )

        for item in response.get("data", []):
            yield {
                "asset_id": asset_id,
                "stake_address": item["account"],
                "amount": int(item["amount"]),
            }

        cursor = response.get("next_cursor")

        if not cursor:
            break


def get_collection_assets(policy_id: str, api_key: str) -> Tuple[str, dict]:
    check_str(policy_id, "gomaestro.policy_id")
    policy_id = policy_id.strip().lower()

    cursor = None

    while True:
        response, status_code = get(
            f"policy/{policy_id}/assets",
            params={
                "cursor": cursor,
            },
            api_key=api_key,
        )

        for item in response.get("data", []):
            quantity = int(item["total_supply"])

            if quantity == 0:
                continue

            yield item

        cursor = response.get("next_cursor")

        if not cursor:
            break


@lru_cache(maxsize=None)
def get_asset_data(asset_id: str, api_key: str) -> dict:
    check_str(asset_id, "gomaestro.asset_id")

    asset_id = asset_id.strip().lower()

    response, status_code = get(
        f"assets/{asset_id}",
        api_key=api_key,
    )

    cip25_metadata = response["data"]["asset_standards"].get("cip25_metadata")
    cip68_metadata = response["data"]["asset_standards"].get("cip68_metadata")

    return cip68_metadata or cip25_metadata


@lru_cache(maxsize=None)
def get_stake_address(address: str, api_key: str) -> str:
    check_str(address, "gomaestro.address")

    response, status_code = get(
        f"addresses/{address}/decode",
        api_key=api_key,
    )

    try:
        return response["staking_cred"]["reward_address"]
    except:
        return address


@lru_cache(maxsize=None)
def get_handle(stake_address: str, api_key: str) -> str:
    check_str(stake_address, "gomaestro.stake_address")

    handles = []

    for holding in get_account_assets(stake_address, api_key=api_key, policy_id=ADA_HANDLE_POLICY_ID):
        asset_id = holding["unit"]
        asset_id = asset_id.replace(f"{ADA_HANDLE_POLICY_ID}000de140", "")  # CIP-68
        asset_id = asset_id.replace(ADA_HANDLE_POLICY_ID, "")  # CIP-25

        asset_name = bytes.fromhex(asset_id).decode()
        handles.append(asset_name)

    if not handles:
        return None

    return sorted(handles, key=len)[0]


@lru_cache(maxsize=None)
def resolve_handle(handle: str, api_key: str) -> str:
    check_str(handle, "gomaestro.handle")

    if handle.startswith("$"):
        if handle.startswith("$"):
            handle = handle[1:]

    handle = handle.lower()

    wallet = resolve_cip25_handle(handle, api_key)

    if wallet:
        return wallet

    return resolve_cip68_handle(handle, api_key)


def resolve_cip25_handle(handle: str, api_key: str) -> str:
    check_str(handle, "gomaestro.handle")

    encoded_name = base64.b16encode(handle.encode()).decode("utf-8")

    asset_id = f"{ADA_HANDLE_POLICY_ID}{encoded_name}".lower()
    owners = list(get_asset_owners(asset_id, api_key))

    if not owners:
        return None

    owner = owners[0]
    owner["cip"] = 25

    return owner


def resolve_cip68_handle(handle: str, api_key: str) -> str:
    check_str(handle, "gomaestro.handle")

    encoded_name = base64.b16encode(handle.encode()).decode("utf-8")

    asset_id = f"{ADA_HANDLE_POLICY_ID}000de140{encoded_name}".lower()
    owners = list(get_asset_owners(asset_id, api_key))

    if not owners:
        return None

    owner = owners[0]
    owner["cip"] = 68

    return owner
