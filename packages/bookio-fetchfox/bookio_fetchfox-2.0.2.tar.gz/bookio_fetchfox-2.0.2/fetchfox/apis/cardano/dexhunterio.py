from typing import Iterable

from fetchfox import rest

ADA = "000000000000000000000000000000000000000000000000000000006c6f76656c616365"
BASE_URL = "https://dexhunter.sbase.ch/"


def get(service: str, partner_code: str, params: dict = None) -> dict:
    url = f"{BASE_URL}/{service}"

    response, _ = rest.get(
        url=url,
        params=params,
        headers={
            "X-Partner-Id": partner_code,
        },
    )

    return response


def post(service: str, body: dict, partner_code: str, params: dict = None) -> dict:
    url = f"{BASE_URL}/{service}"

    response, _ = rest.post(
        url=url,
        params=params,
        body=body,
        headers={
            "X-Partner-Id": partner_code,
        },
    )

    return response


def get_asset_orders(asset_id: str, partner_code: str) -> Iterable[dict]:
    body = {
        "filters": [
            {
                "filterType": "TOKENID",
                "values": [asset_id],
            },
            {
                "filterType": "STATUS",
                "values": ["COMPLETED"],
            },
        ],
        "orderSorts": "STARTTIME",
        "page": 0,
        "perPage": 100,
        "sortDirection": "DESC",
    }

    page = -1

    while True:
        page += 1
        body["page"] = page

        response = post(
            "swap/globalOrders",
            body=body,
            partner_code=partner_code,
        )

        if not response.get("orders"):
            break

        yield from response["orders"]


def get_asset_average_price(asset_id: str, partner_code: str) -> float:
    response = get(
        f"swap/averagePrice/{asset_id}/ADA",
        partner_code=partner_code,
    )

    return response["average_price"]


def get_asset_pair_stats(asset_id: str, partner_code: str) -> dict:
    return get(
        f"swap/pairStats/{asset_id}/ADA",
        partner_code=partner_code,
    )
