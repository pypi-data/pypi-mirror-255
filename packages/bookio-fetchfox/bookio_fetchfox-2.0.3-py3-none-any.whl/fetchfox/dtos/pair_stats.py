class StatsDTO:
    def __init__(
        self,
        ada: float,
        book: float,
        daily_txs: int,
        daily_buys: int,
        daily_sales: int,
        daily_volume: float,
        # price_change_hour: float,
        price_change_day: float,
        # price_change_week: float,
        # price_change_month: float,
    ):
        self.ada: float = ada
        self.book: float = book
        self.daily_txs: int = daily_txs
        self.daily_buys: int = daily_buys
        self.daily_sales: int = daily_sales
        self.daily_volume: float = daily_volume
        # self.price_change_hour: float = price_change_hour
        self.price_change_day: float = price_change_day
        # self.price_change_week: float = price_change_week
        # self.price_change_month: float = price_change_month

    def __repr__(self):
        return f"{round(self.ada)} ADA - {round(self.book)} BOOK"


class PairStatsDTO:
    def __init__(self, stats: StatsDTO):
        self.stats: StatsDTO = stats
        # self.pools: Dict[StatsDTO] = {}

    # def add_pool(self, name: str, stats: StatsDTO):
    #     self.pools[name.lower()] = stats

    def __repr__(self):
        return f"{self.stats}"
