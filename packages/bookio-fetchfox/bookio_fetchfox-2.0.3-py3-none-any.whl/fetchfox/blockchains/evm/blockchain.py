import json
import logging
from datetime import datetime
from typing import Iterable, Tuple, List

import pytz

from fetchfox.apis import bookio
from fetchfox.apis.evm import moralisio, ensideascom, openseaio
from fetchfox.blockchains.base import Blockchain
from fetchfox.constants.blockchains import ETHEREUM
from fetchfox.constants.marketplaces import OPENSEA_IO
from fetchfox.dtos import (
    AssetDTO,
    CampaignDTO,
    CampaignPricingDTO,
    FloorDTO,
    HoldingDTO,
    ListingDTO,
    SaleDTO,
)
from fetchfox.helpers import formatters
from . import utils
from .exceptions import (
    InvalidEvmAssetIdException,
    InvalidEvmCollectionIdException,
    InvalidEvmAccountException,
)

logger = logging.getLogger(__name__)


class Evm(Blockchain):
    def __init__(self, name: str, currency: str, logo: str, moralisio_api_key: str = None, openseaio_api_key: str = None):
        super().__init__(name, currency, logo)

        self.moralisio_api_key: str = moralisio_api_key
        self.openseaio_api_key: str = openseaio_api_key

    def check_account(self, account: str):
        if not utils.is_account(account):
            raise InvalidEvmAccountException(account, self.name)

    def check_asset_id(self, asset_id: str):
        if not utils.is_asset_id(asset_id):
            raise InvalidEvmAssetIdException(asset_id, self.name)

    def check_collection_id(self, collection_id: str):
        if not utils.is_address(collection_id):
            raise InvalidEvmCollectionIdException(collection_id, self.name)

    # Accounts

    def get_account_assets(self, wallet: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_account(wallet)

        if utils.is_ens_domain(wallet):
            wallet = ensideascom.resolve_ens_domain(wallet)

        account_assets = moralisio.get_account_assets(
            wallet,
            blockchain=self.name,
            api_key=self.moralisio_api_key,
        )

        for asset in account_assets:
            yield HoldingDTO(
                collection_id=asset["token_address"],
                asset_id=asset["token_id"],
                address=wallet,
                quantity=int(asset["amount"]),
            )

    def get_account_balance(self, wallet: str) -> Tuple[float, str]:
        self.check_account(wallet)

        if utils.is_ens_domain(wallet):
            wallet = ensideascom.resolve_ens_domain(wallet)

        balance = moralisio.get_account_balance(
            wallet,
            blockchain=self.name,
            api_key=self.moralisio_api_key,
        )

        return balance, self.currency

    def get_account_name(self, account: str) -> str:
        if utils.is_ens_domain(account):
            return account

        if utils.is_address(account):
            return ensideascom.get_ens_domain(account)

        return None

    def resolve_account_name(self, name: str) -> str:
        if utils.is_ens_domain(name):
            return ensideascom.resolve_ens_domain(name)

        return None

    # Assets

    def get_asset(self, collection_id: str, asset_id: str, *args, **kwargs) -> AssetDTO:
        self.check_collection_id(collection_id)
        self.check_asset_id(asset_id)

        asset_data = moralisio.get_asset_data(
            contract_address=collection_id,
            asset_id=asset_id,
            blockchain=self.name,
            api_key=self.moralisio_api_key,
        )

        metadata = json.loads(asset_data["metadata"])
        metadata["attributes"].update(metadata["extraAttributes"])

        return AssetDTO(
            collection_id=collection_id,
            asset_id=asset_id,
            metadata=metadata,
        )

    def get_asset_owners(self, collection_id: str, asset_id: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_collection_id(collection_id)
        self.check_asset_id(asset_id)

        asset_owner = moralisio.get_asset_owner(
            collection_id,
            asset_id=asset_id,
            blockchain=self.name,
            api_key=self.moralisio_api_key,
        )

        yield HoldingDTO(
            collection_id=asset_owner["contract_address"],
            asset_id=asset_owner["asset_id"],
            address=asset_owner["address"],
            quantity=asset_owner["amount"],
        )

    # Collections

    def get_collection_assets(self, collection_id: str, fetch_metadata: bool = True, *args, **kwargs) -> Iterable[AssetDTO]:
        self.check_collection_id(collection_id)

        if fetch_metadata:
            asset_id = -1

            while True:
                try:
                    asset_id += 1

                    yield self.get_asset(
                        collection_id=collection_id,
                        asset_id=str(asset_id),
                    )
                except ValueError:
                    raise
                except:
                    break
        else:
            collection_assets = moralisio.get_collection_assets(
                contract_address=collection_id,
                blockchain=self.name,
                api_key=self.moralisio_api_key,
            )

            for asset_id in collection_assets:
                yield AssetDTO(
                    collection_id=collection_id,
                    asset_id=asset_id,
                    metadata={},
                )

    def get_collection_floor(self, collection_id: str, *args, **kwargs) -> FloorDTO:
        self.check_collection_id(collection_id)

        floor = None
        count = 0

        for listing in self.get_collection_listings(collection_id):
            count += 1

            if floor is None:
                floor = listing
            elif listing.usd < floor.usd:
                floor = listing

        return FloorDTO(
            listing=floor,
            listing_count=count,
        )

    def get_collection_listings(self, collection_id: str, slug: str = None, *args, **kwargs) -> Iterable[ListingDTO]:
        self.check_collection_id(collection_id)

        collection_listings = openseaio.get_collection_listings(
            collection_id,
            blockchain=self.name,
            api_key=self.openseaio_api_key,
            slug=slug,
        )

        for listing in collection_listings:
            protocol_data = listing["protocol_data"]
            parameters = protocol_data["parameters"]

            price = listing["price"]["current"]

            asset_ids = []
            asset_names = []

            for offer in parameters["offer"]:
                if offer["token"].lower() != collection_id.lower():
                    continue

                asset_ids.append(offer["identifierOrCriteria"])
                asset_names.append("")

            if listing.get("eventTimestamp"):
                listed_at = datetime.utcfromtimestamp(parameters["startTime"])
            else:
                listed_at = datetime.now(tz=pytz.utc)

            marketplace_url = self.marketplace_url(
                collection_id=collection_id,
                asset_id=asset_ids[0],
            )

            yield ListingDTO(
                identifier=listing["order_hash"],
                collection_id=collection_id,
                asset_ids=asset_ids,
                asset_names=asset_names,
                listing_id=listing["order_hash"],
                marketplace=OPENSEA_IO,
                price=float(int(price["value"]) / 10 ** price["decimals"]),
                currency=price["currency"].replace("WETH", "ETH"),
                listed_at=listed_at,
                listed_by=parameters["offerer"],
                tx_hash=listing["order_hash"],
                marketplace_url=marketplace_url,
            )

    def get_collection_sales(self, collection_id: str, slug: str = None, *args, **kwargs) -> Iterable[SaleDTO]:
        self.check_collection_id(collection_id)

        collection_sale = openseaio.get_collection_sales(
            collection_id,
            blockchain=self.name,
            api_key=self.openseaio_api_key,
            slug=slug,
        )

        for sale in collection_sale:
            tx_hash = sale["transaction"]

            asset = sale["nft"]
            asset_id = asset["identifier"]
            asset_name = asset["name"]

            if sale.get("closing_date"):
                confirmed_at = datetime.fromtimestamp(
                    sale["closing_date"],
                    tz=pytz.utc,
                )
            else:
                confirmed_at = datetime.now(
                    tz=pytz.utc,
                )

            marketplace_url = self.marketplace_url(
                collection_id=collection_id,
                asset_id=asset_id,
            )

            explorer_url = self.explorer_url(
                tx_hash=tx_hash,
            )

            yield SaleDTO(
                identifier=f"{tx_hash}/{asset_id}",
                collection_id=collection_id,
                asset_ids=[asset_id],
                asset_names=[asset_name],
                tx_hash=tx_hash,
                marketplace=OPENSEA_IO,
                price=float(int(sale["payment"]["quantity"]) / 10 ** sale["payment"]["decimals"]),
                currency=sale["payment"]["symbol"].replace("WETH", "ETH"),
                confirmed_at=confirmed_at,
                sold_by=sale["seller"],
                bought_by=sale["buyer"],
                sale_id=sale["transaction"],
                marketplace_url=marketplace_url,
                explorer_url=explorer_url,
            )

    def get_collection_snapshot(self, collection_id: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_collection_id(collection_id)

        collection_owners = moralisio.get_collection_owners(
            collection_id,
            blockchain=self.name,
            api_key=self.moralisio_api_key,
        )

        for asset in collection_owners:
            yield HoldingDTO(
                collection_id=asset["contract_address"],
                asset_id=asset["asset_id"],
                address=asset["address"],
                quantity=asset["amount"],
            )

    def get_campaigns(self, starts_after: datetime = None) -> Iterable[CampaignDTO]:
        def parse_pricing(pricing: dict) -> List[CampaignPricingDTO]:
            result = []

            if pricing.get("native_price"):
                result.append(
                    CampaignPricingDTO(
                        currency=self.currency,
                        amount=pricing["native_price"] / 10**18,
                    )
                )

            return result

        for campaign in bookio.get_campaigns():
            if not campaign.get("collection_id"):
                continue

            if campaign["blockchain"] != "evm":
                continue

            network = "mainnet" if self.name == ETHEREUM else self.name

            if campaign["network"] != network:
                continue

            collection_id = campaign["collection_id"]
            start_at = formatters.timestamp(campaign["start_at"])

            if starts_after is not None:
                if start_at < starts_after:
                    continue

            yield CampaignDTO(
                blockchain=self.name,
                parlamint_id=campaign["campaign_id"],
                collection_id=collection_id,
                name=campaign["name"],
                start_at=start_at,
                supply=campaign["total_deas"],
                limit=campaign["max_quantity"],
                mint_pricing=parse_pricing(
                    pricing=campaign.get("mint_price", {}),
                ),
                discount_pricing=parse_pricing(
                    pricing=campaign.get("discount_price", {}),
                ),
                bookstore_url=campaign["bookstore_url"],
                cover_url=campaign["cover_url"],
                explorer_url=self.explorer_url(
                    collection_id=collection_id,
                ),
            )
