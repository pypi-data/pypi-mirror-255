from typing import Iterable, Tuple

from cachetools.func import ttl_cache

from fetchfox.apis import price
from fetchfox.apis.cardano import cexplorerio, dexhunterio
from fetchfox.constants.book import (
    BOOK_TOKEN_ASSET_ID,
    BOOK_TOKEN_ASSET_NAME,
    BOOK_TOKEN_COINGECKO_ID,
    BOOK_TOKEN_POLICY_ID,
    BOOK_TOKEN_FINGERPRINT,
)
from fetchfox.constants.currencies import ADA, BOOK
from fetchfox.dtos import OrderDTO, OrderType, PairStatsDTO, StatsDTO


class BookToken:
    asset_id = BOOK_TOKEN_ASSET_ID
    asset_name = BOOK_TOKEN_ASSET_NAME
    coingecko_id = BOOK_TOKEN_COINGECKO_ID
    fingerprint = BOOK_TOKEN_FINGERPRINT
    policy_id = BOOK_TOKEN_POLICY_ID
    symbol = BOOK

    def __init__(self, dexhunter_partner_code: str):
        self.dexhunter_partner_code = dexhunter_partner_code

    @property
    @ttl_cache(ttl=30)
    def ada(self) -> float:
        return dexhunterio.get_asset_average_price(
            self.asset_id,
            partner_code=self.dexhunter_partner_code,
        )

    @property
    @ttl_cache(ttl=30)
    def usd(self) -> float:
        return price.usd(ADA) * self.ada

    @property
    @ttl_cache(ttl=30)
    def ath_usd(self) -> float:
        return price.ath_usd(BOOK)

    @property
    def cardanoscan_url(self):
        return f"https://cardanoscan.io/token/{self.asset_id}"

    @property
    def cexplorer_url(self):
        return f"https://cexplorer.io/asset/{self.fingerprint}"

    @property
    def coingecko_url(self):
        return f"https://www.coingecko.com/en/coins/{self.coingecko_id}"

    @property
    def dexhunter_url(self):
        return f"https://app.dexhunter.io/trends?asset={self.asset_id}&status=COMPLETED"

    @property
    def minswap_url(self):
        return f"https://app.minswap.org/swap?currencySymbolA={self.policy_id}&tokenNameA={self.asset_name}&currencySymbolB=&tokenNameB="

    @property
    def taptools_url(self):
        return "https://www.taptools.io/charts/token?pairID=0be55d262b29f564998ff81efe21bdc0022621c12f15af08d0f2ddb1.2ed309a7ecb6d0d5e00dca0bcc3924fdc0627a5fb631f1acc4deb898b14ee8bd"

    @property
    def owners(self) -> Tuple[int, int]:
        tx = cexplorerio.get_asset_detail(self.fingerprint)

        return tx["epoch"], tx["owners_acc"]

    @property
    def pair_stats(self) -> PairStatsDTO:
        stats = dexhunterio.get_asset_pair_stats(
            self.asset_id,
            partner_code=self.dexhunter_partner_code,
        )

        stats_dto = StatsDTO(
            ada=stats["token2Amount"],
            book=stats["token1Amount"],
            daily_txs=stats["dailyTxAmount"],
            daily_buys=stats["dailyBuysCount"],
            daily_sales=stats["dailySalesCount"],
            daily_volume=stats["dailyVolume"],
            price_change_day=stats["priceChangeDay"],
        )

        return PairStatsDTO(stats_dto)

    def last_orders(self, limit: int = 25) -> Iterable[OrderDTO]:
        orders = dexhunterio.get_asset_orders(
            self.asset_id,
            partner_code=self.dexhunter_partner_code,
        )

        for index, order in enumerate(orders):
            if index == limit:
                break

            if order["token_id_in"] == dexhunterio.ADA:
                order_type = OrderType.BUY
                ada = order["amount_in"]
                book = order["actual_out_amount"]
            else:
                order_type = OrderType.SELL
                book = order["amount_in"]
                ada = order["actual_out_amount"]

            yield OrderDTO(
                address=order["user_address"],
                ada=ada,
                book=book,
                order_type=order_type,
                dex=order["dex"],
                tx_hash=order.get("update_tx_hash") or order["tx_hash"],
            )
