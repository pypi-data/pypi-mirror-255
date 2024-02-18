from fetchfox import rest

BASE_URL = "https://js.cexplorer.io/api-static"


def get_asset_detail(fingerprint: str) -> dict:
    url = f"{BASE_URL}/asset/detail/{fingerprint}.json"

    response, status_code = rest.get(url)

    return response["data"]["tx"]
