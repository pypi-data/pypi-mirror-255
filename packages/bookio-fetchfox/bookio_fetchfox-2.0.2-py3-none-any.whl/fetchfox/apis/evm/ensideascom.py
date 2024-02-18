import logging
from functools import lru_cache
from typing import Tuple

from fetchfox import rest
from fetchfox.checks import check_str

BASE_URL = "https://api.ensideas.com"

logger = logging.getLogger(__name__)


def get(service: str, params: dict = None) -> Tuple[dict, int]:
    return rest.get(
        url=f"{BASE_URL}/{service}",
        params=params,
    )


@lru_cache(maxsize=None)
def resolve_ens_domain(ens_domain: str):
    check_str(ens_domain)

    response, status_code = get(f"ens/resolve/{ens_domain}")

    address = response.get("address")

    if not address:
        return None

    logger.info("resolved %s to %s", ens_domain, address)
    return address


@lru_cache(maxsize=None)
def get_ens_domain(address: str):
    check_str(address)

    response, status_code = get(f"ens/resolve/{address}")

    ens_domain = response.get("name")

    if not ens_domain:
        return None

    logger.info("resolved %s to %s", address, ens_domain)
    return ens_domain
