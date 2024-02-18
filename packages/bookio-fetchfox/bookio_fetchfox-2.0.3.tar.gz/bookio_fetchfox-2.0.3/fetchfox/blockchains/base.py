from abc import abstractmethod
from datetime import datetime
from typing import Iterable, Tuple

from fetchfox.apis import price
from fetchfox.dtos import (
    AssetDTO,
    CampaignDTO,
    FloorDTO,
    HoldingDTO,
    ListingDTO,
    RankDTO,
    SaleDTO,
)


class Blockchain:
    def __init__(self, name: str, currency: str, logo: str):
        self.name: str = name
        self.currency: str = currency
        self.logo: str = logo

    @property
    def usd(self) -> float:
        return price.usd(self.currency)

    @abstractmethod
    def check_account(self, account: str):
        raise NotImplementedError()

    @abstractmethod
    def check_collection_id(self, collection_id: str):
        raise NotImplementedError()

    @abstractmethod
    def check_asset_id(self, asset_id: str):
        raise NotImplementedError()

    @abstractmethod
    def explorer_url(self, *, address: str = None, collection_id: str = None, asset_id: str = None, tx_hash: str = None) -> str:
        raise NotImplementedError()

    @abstractmethod
    def marketplace_url(self, *, collection_id: str = None, asset_id: str = None) -> str:
        raise NotImplementedError()

    # Accounts

    @abstractmethod
    def get_account_assets(self, wallet: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        raise NotImplementedError()

    @abstractmethod
    def get_account_balance(self, account: str) -> Tuple[float, str]:
        raise NotImplementedError()

    @abstractmethod
    def get_account_name(self, account: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def resolve_account_name(self, account: str) -> str:
        raise NotImplementedError()

    def format_account(self, account: str) -> str:
        self.check_account(account)

        name = self.get_account_name(account)

        if name:
            return name

        return f"{account[:5]}..{account[-5:]}"

    # Assets

    @abstractmethod
    def get_asset(self, collection_id: str, asset_id: str, *args, **kwargs) -> AssetDTO:
        raise NotImplementedError()

    @abstractmethod
    def get_asset_owners(self, collection_id: str, asset_id: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        raise NotImplementedError()

    def get_asset_rank(self, collection_id: str, asset_id: str, *args, **kwargs) -> RankDTO:
        return None

    # Collections

    @abstractmethod
    def get_collection_assets(self, collection_id: str, fetch_metadata: bool = True, *args, **kwargs) -> Iterable[AssetDTO]:
        raise NotImplementedError()

    @abstractmethod
    def get_collection_floor(self, collection_id: str, *args, **kwargs) -> FloorDTO:
        raise NotImplementedError()

    @abstractmethod
    def get_collection_listings(self, collection_id: str, *args, **kwargs) -> Iterable[ListingDTO]:
        raise NotImplementedError()

    def get_collection_ranks(self, collection_id: str, *args, **kwargs) -> Iterable[RankDTO]:
        return []

    @abstractmethod
    def get_collection_sales(self, collection_id: str, *args, **kwargs) -> Iterable[SaleDTO]:
        raise NotImplementedError()

    @abstractmethod
    def get_collection_snapshot(self, collection_id: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        raise NotImplementedError()

    # Campaigns

    def get_campaigns(self, starts_after: datetime = None) -> Iterable[CampaignDTO]:
        raise NotImplementedError()
