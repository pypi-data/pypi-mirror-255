import logging
import time

from cachetools.func import ttl_cache

from fetchfox import rest
from fetchfox.constants.currencies import ALGO, ADA, BOOK, ETH, MATIC

IDS = {
    ALGO: "algorand",
    ADA: "cardano",
    BOOK: "book-2",
    ETH: "ethereum",
    MATIC: "matic-network",
}

logger = logging.getLogger(__name__)


@ttl_cache(ttl=60 * 60)
def get_currency_usd_exchange(currency: str):
    time.sleep(5)

    currency = currency.strip().upper()

    id = IDS[currency]

    logger.info("fetching exchange for %s (%s)", currency, id)

    response, status_code = rest.get(
        url="https://api.coingecko.com/api/v3/simple/price",
        params={
            "ids": id,
            "vs_currencies": "usd",
        },
    )

    return response[id]["usd"]


@ttl_cache(ttl=60 * 60)
def get_currency_ath_usd(currency: str):
    time.sleep(5)

    currency = currency.strip().upper()

    id = IDS[currency]

    logger.info("fetching ath for %s (%s)", currency, id)

    response, status_code = rest.get(
        url=f"https://api.coingecko.com/api/v3/coins/{id}",
    )

    return response["market_data"]["ath"]["usd"]
