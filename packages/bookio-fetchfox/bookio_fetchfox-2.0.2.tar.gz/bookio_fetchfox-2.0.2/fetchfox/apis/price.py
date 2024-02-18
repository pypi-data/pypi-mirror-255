from fetchfox.apis import coingeckocom


def usd(currency: str) -> float:
    return coingeckocom.get_currency_usd_exchange(currency)


def ath_usd(currency: str) -> float:
    return coingeckocom.get_currency_ath_usd(currency)
