import logging
from datetime import datetime
from typing import Iterable, Tuple, List

import pytz

from fetchfox.apis import bookio
from fetchfox.apis.cardano import cnfttools, jpgstore, gomaestroorg
from fetchfox.blockchains.base import Blockchain
from fetchfox.constants.blockchains import CARDANO
from fetchfox.constants.currencies import ADA, BOOK
from fetchfox.constants.marketplaces import JPG_STORE
from fetchfox.dtos import (
    AssetDTO,
    CampaignDTO,
    CampaignPricingDTO,
    FloorDTO,
    HoldingDTO,
    ListingDTO,
    RankDTO,
    SaleDTO,
    SaleType,
)
from fetchfox.helpers import formatters
from . import utils
from .exceptions import (
    InvalidCardanoAssetIdException,
    InvalidCardanoCollectionIdException,
    InvalidCardanoAccountException,
)

WINTER_NFT_ADDRESS = "addr1qxnrv2quqxhvwxtxmygsmkufph4kjju6j5len7k2ljslpz8ql7k7gehlfvj6ektgu9ns8yx8epcp66337khxeq82rpgqe6lqyk"

logger = logging.getLogger(__name__)


class Cardano(Blockchain):
    def __init__(self, maestro_api_key: str = None):
        super().__init__(
            name=CARDANO,
            currency=ADA,
            logo="https://s2.coinmarketcap.com/static/img/coins/64x64/2010.png",
        )

        self.maestro_api_key: str = maestro_api_key

    def check_account(self, account: str):
        if not utils.is_account(account):
            raise InvalidCardanoAccountException(account)

    def check_asset_id(self, asset_id: str):
        if not utils.is_asset_id(asset_id):
            raise InvalidCardanoAssetIdException(asset_id)

    def check_collection_id(self, collection_id: str):
        if not utils.is_policy_id(collection_id):
            raise InvalidCardanoCollectionIdException(collection_id)

    def explorer_url(self, *, address: str = None, collection_id: str = None, asset_id: str = None, tx_hash: str = None) -> str:
        if address:
            return f"https://pool.pm/{address.lower()}"

        if asset_id:
            return f"https://cardanoscan.io/token/{asset_id.lower()}"

        if collection_id:
            return f"https://pool.pm/policy/{collection_id.lower()}"

        if tx_hash:
            return f"https://cardanoscan.io/transaction/{tx_hash.lower()}"

        return None

    def marketplace_url(self, collection_id: str = None, asset_id: str = None) -> str:
        if asset_id:
            return f"https://www.jpg.store/asset/{asset_id.lower()}"

        if collection_id:
            return f"https://jpg.store/collection/{collection_id.lower()}"

        return None

    # Accounts

    def get_account_assets(self, wallet: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_account(wallet)

        stake_address = self.get_account_stake_address(wallet)

        account_assets = gomaestroorg.get_account_assets(
            stake_address,
            api_key=self.maestro_api_key,
        )

        for account_asset in account_assets:
            asset_id = account_asset["unit"]
            quantity = account_asset["amount"]

            try:
                policy_id, _ = utils.split_asset_id(asset_id)
            except UnicodeDecodeError:
                continue

            yield HoldingDTO(
                collection_id=policy_id,
                asset_id=asset_id,
                address=stake_address,
                quantity=quantity,
            )

    def get_account_name(self, account: str) -> str:
        if utils.is_ada_handle(account):
            return account

        if utils.is_address(account):
            account = self.get_account_stake_address(account)

        return gomaestroorg.get_handle(
            account,
            api_key=self.maestro_api_key,
        )

    def get_account_balance(self, wallet: str) -> Tuple[float, str]:
        stake_address = self.get_account_stake_address(wallet)

        balance = gomaestroorg.get_account_balance(
            stake_address,
            api_key=self.maestro_api_key,
        )

        return balance, self.currency

    def resolve_account_name(self, name: str) -> str:
        if not utils.is_ada_handle(name):
            return None

        resolution = gomaestroorg.resolve_handle(
            name,
            api_key=self.maestro_api_key,
        )

        if not resolution:
            return None

        return resolution["stake_address"]

    def get_account_stake_address(self, account: str) -> str:
        self.check_account(account)

        if utils.is_stake_address(account):
            return account

        if utils.is_address(account):
            return gomaestroorg.get_stake_address(
                account,
                api_key=self.maestro_api_key,
            )

        if utils.is_ada_handle(account):
            resolution = gomaestroorg.resolve_handle(
                account,
                api_key=self.maestro_api_key,
            )

            return resolution["stake_address"]

        return None

    # Assets

    def format_account(self, account: str) -> str:
        self.check_account(account)

        handle = self.get_account_name(account)

        if handle:
            punycode = handle.encode().decode("idna")

            if handle != punycode:
                return f"{punycode} (${handle})"

            return f"${handle}"

        return super().format_account(account)

    def get_asset(self, collection_id: str, asset_id: str, *args, **kwargs) -> AssetDTO:
        self.check_collection_id(collection_id)
        self.check_asset_id(asset_id)

        asset_data = gomaestroorg.get_asset_data(
            asset_id,
            api_key=self.maestro_api_key,
        )

        return AssetDTO(
            collection_id=collection_id,
            asset_id=asset_id,
            metadata=asset_data,
        )

    def get_asset_owners(self, collection_id: str, asset_id: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_collection_id(collection_id)
        self.check_asset_id(asset_id)

        asset_owners = gomaestroorg.get_asset_owners(
            asset_id,
            api_key=self.maestro_api_key,
        )

        for owner in asset_owners:
            yield HoldingDTO(
                collection_id=collection_id,
                asset_id=owner["asset_id"],
                address=owner["stake_address"],
                quantity=owner["amount"],
            )

    def get_asset_rank(self, collection_id: str, asset_id: str, *args, **kwargs) -> RankDTO:
        self.check_collection_id(collection_id)
        self.check_asset_id(asset_id)

        asset_rank = cnfttools.get_asset_rank(asset_id)

        if asset_rank is None:
            return None

        _, asset_name = utils.split_asset_id(asset_id)
        number = int("".join((c for c in asset_name if c.isdigit())))

        return RankDTO(
            collection_id=collection_id,
            asset_id=asset_id.lower(),
            number=number,
            rank=int(asset_rank),
        )

    # Collections

    def get_collection_assets(
        self, collection_id: str, discriminator: str = None, fetch_metadata: bool = True, *args, **kwargs
    ) -> Iterable[AssetDTO]:
        self.check_collection_id(collection_id)

        collection_assets = gomaestroorg.get_collection_assets(
            collection_id,
            api_key=self.maestro_api_key,
        )

        for asset in collection_assets:
            encoded_asset_name = asset["asset_name"]
            asset_id = f"{collection_id}{encoded_asset_name}"
            cip25_metadata = asset["asset_standards"].get("cip25_metadata")
            cip68_metadata = asset["asset_standards"].get("cip68_metadata")

            policy_id, asset_name = utils.split_asset_id(asset_id)

            # required for multi-book policies (e.g. monsters, greek classics)
            if discriminator:
                if discriminator not in asset_name.lower():
                    continue

            yield AssetDTO(
                collection_id=collection_id,
                asset_id=asset_id,
                metadata=cip68_metadata or cip25_metadata,
            )

    def get_collection_floor(self, collection_id: str, discriminator: str = None, *args, **kwargs) -> FloorDTO:
        self.check_collection_id(collection_id)

        collection_listings = self.get_collection_listings(
            collection_id,
            discriminator=discriminator,
        )

        floor = None
        count = 0

        for listing in collection_listings:
            count += 1

            if floor is None:
                floor = listing
            elif listing.usd < floor.usd:
                floor = listing

        return FloorDTO(
            listing=floor,
            listing_count=count,
        )

    def get_collection_listings(self, collection_id: str, discriminator: str = None, *args, **kwargs) -> Iterable[ListingDTO]:
        self.check_collection_id(collection_id)

        if discriminator:
            discriminator = discriminator.lower()

        collection_listings = jpgstore.get_collection_listings(collection_id)

        for listing in collection_listings:
            asset_id = listing["asset_id"]
            policy_id, asset_name = utils.split_asset_id(asset_id)

            # required for multi-book policies (e.g. monsters, greek classics)
            if discriminator:
                if discriminator not in asset_name.lower():
                    continue

            asset_ids = []
            asset_names = []

            if listing["listing_type"] == "BUNDLE":
                for bundled_asset in listing["bundled_assets"]:
                    asset_ids.append(bundled_asset["asset_id"])
                    asset_names.append(bundled_asset["display_name"])
            else:
                asset_ids.append(listing["asset_id"])
                asset_names.append(listing["display_name"])

            if listing.get("confirmed_at"):
                listed_at = datetime.fromisoformat(listing["confirmed_at"].replace("Z", "+00:00"))
            else:
                listed_at = datetime.now(tz=pytz.utc)

            yield ListingDTO(
                identifier=listing["tx_hash"],
                collection_id=policy_id,
                asset_ids=asset_ids,
                asset_names=asset_names,
                listing_id=listing["listing_id"],
                marketplace=JPG_STORE,
                price=int(listing["price_lovelace"]) // 10**6,
                currency=self.currency,
                listed_at=listed_at,
                listed_by=None,
                tx_hash=listing["tx_hash"],
                marketplace_url=f"https://jpg.store/asset/{asset_id}",
            )

    def get_collection_ranks(self, collection_id: str, *args, **kwargs) -> Iterable[RankDTO]:
        self.check_collection_id(collection_id)

        collection_ranks = cnfttools.get_collection_ranks(collection_id) or {}

        for asset_name, rank in collection_ranks.items():
            number = int("".join((c for c in asset_name if c.isdigit())))

            yield RankDTO(
                collection_id=collection_id,
                number=number,
                asset_id=None,
                rank=int(rank),
            )

    def get_collection_sales(self, collection_id: str, discriminator: str = None, *args, **kwargs) -> Iterable[SaleDTO]:
        self.check_collection_id(collection_id)

        collection_sales = jpgstore.get_collection_sales(collection_id)

        for sale in collection_sales:
            tx_hash = sale["tx_hash"]

            asset_id = sale["asset_id"]
            policy_id, asset_name = utils.split_asset_id(asset_id)

            # required for multi-book policies (e.g. monsters, greek classics)
            if discriminator:
                if discriminator not in asset_name.lower():
                    continue

            bulk_size = sale.get("bulk_size", None) or 1

            if sale["action"] == "ACCEPT_OFFER":
                buyer = sale["seller_address"]
                seller = sale["signer_address"]
                sale_type = SaleType.OFFER
            elif sale["action"] == "ACCEPT_COLLECTION_OFFER":
                buyer = sale["signer_address"]
                seller = sale["seller_address"]
                sale_type = SaleType.COLLECTION_OFFER
            elif sale["action"] == "BUY":
                buyer = sale["signer_address"]
                seller = sale["seller_address"]

                if buyer == WINTER_NFT_ADDRESS:
                    sale_type = SaleType.CREDIT_CARD
                else:
                    sale_type = SaleType.PURCHASE
            else:
                continue

            asset_ids = []
            asset_names = []

            if sale["listing_from_tx_history"]["bundled_assets"]:
                for bundled_asset in sale["listing_from_tx_history"]["bundled_assets"]:
                    asset_ids.append(bundled_asset["asset_id"])
                    asset_names.append(bundled_asset["display_name"])
            else:
                asset_ids.append(sale["asset_id"])
                asset_names.append(sale["display_name"])

            if sale.get("confirmed_at"):
                confirmed_at = datetime.fromisoformat(sale["confirmed_at"].replace("Z", "+00:00"))
            else:
                confirmed_at = datetime.now(tz=pytz.utc)

            yield SaleDTO(
                identifier=tx_hash,
                collection_id=policy_id,
                asset_ids=asset_ids,
                asset_names=asset_names,
                tx_hash=tx_hash,
                marketplace=JPG_STORE,
                price=int(sale["amount_lovelace"]) // 10**6,
                currency=self.currency,
                confirmed_at=confirmed_at,
                type=sale_type,
                bulk_size=bulk_size,
                sold_by=seller,
                bought_by=buyer,
                marketplace_url=f"https://jpg.store/asset/{asset_id}",
                explorer_url=f"https://cardanoscan.io/transaction/{tx_hash}",
            )

    def get_collection_snapshot(self, collection_id: str, discriminator: str = None, max_threads: int = 3, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_collection_id(collection_id)

        collection_owners = gomaestroorg.get_collection_owners(
            collection_id,
            api_key=self.maestro_api_key,
        )

        for owner in collection_owners:
            stake_address = owner["account"]

            for asset in owner.get("assets", []):
                encoded_asset_name = asset["name"]
                asset_id = f"{collection_id}{encoded_asset_name}"
                quantity = asset["amount"]

                policy_id, asset_name = utils.split_asset_id(asset_id)

                # required for multi-book policies (e.g. monsters, greek classics)
                if discriminator:
                    if discriminator not in asset_name.lower():
                        continue

                yield HoldingDTO(
                    collection_id=collection_id,
                    asset_id=asset_id,
                    address=stake_address,
                    quantity=quantity,
                )

    # Campaigns

    def get_campaigns(self, starts_after: datetime = None) -> Iterable[CampaignDTO]:
        def parse_pricing(pricing: dict) -> List[CampaignPricingDTO]:
            result = []

            if pricing.get("native_price"):
                result.append(
                    CampaignPricingDTO(
                        currency=ADA,
                        amount=pricing["native_price"] / 10**6,
                    )
                )

            if pricing.get("book_token_price"):
                result.append(
                    CampaignPricingDTO(
                        currency=BOOK,
                        amount=pricing["book_token_price"] / 10**6,
                    )
                )

            return result

        for campaign in bookio.get_campaigns():
            if not campaign.get("collection_id"):
                continue

            if campaign["blockchain"] != "cardano":
                continue

            if campaign["network"] != "mainnet":
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
