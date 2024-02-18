from enum import Enum


class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderDTO:
    def __init__(self, address: str, ada: float, book: float, dex: str, tx_hash: str, order_type: OrderType):
        self.address: str = address
        self.ada: float = ada
        self.book: float = book
        self.dex: str = dex.lower()
        self.tx_hash: str = tx_hash
        self.order_type: OrderType = order_type

    @property
    def average(self) -> float:
        return self.ada / self.book

    def __repr__(self):
        if self.order_type == OrderType.BUY:
            return f"{round(self.ada)} ADA > {round(self.book)} BOOK ({self.dex}) [{self.average}]"
        else:
            return f"{round(self.book)} BOOK > {round(self.ada)} ADA ({self.dex}) [{self.average}]"
