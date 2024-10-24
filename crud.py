from typing import Optional

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import CreateItem, CreateShop, Item, Shop
from .wordlists import animals

db = Database("ext_offlineshop")


async def create_shop(data: CreateShop) -> Shop:
    data.wordlist = data.wordlist or "\n".join(animals)
    shop = Shop(id=urlsafe_short_hash(), **data.dict())
    await db.insert("offlineshop.shops", shop)
    return shop


async def get_shop(shop_id: str) -> Optional[Shop]:
    return await db.fetchone(
        "SELECT * FROM offlineshop.shops WHERE id = :id",
        {"id": shop_id},
        Shop,
    )


async def get_or_create_shop_by_wallet(wallet: str) -> Optional[Shop]:
    shop = await db.fetchone(
        "SELECT * FROM offlineshop.shops WHERE wallet = :wallet",
        {"wallet": wallet},
        Shop,
    )
    return shop or await create_shop(CreateShop(wallet=wallet))


async def update_shop(shop: Shop) -> Shop:
    await db.update("offlineshop.shops", shop)
    return shop


async def create_item(
    shop: str,
    data: CreateItem,
) -> Item:
    item = Item(id=urlsafe_short_hash(), shop=shop, **data.dict())
    await db.insert("offlineshop.items", item)
    return item


async def update_item(item: Item) -> Item:
    await db.update("offlineshop.items", item)
    return item


async def get_item(item_id: str) -> Optional[Item]:
    return await db.fetchone(
        "SELECT * FROM offlineshop.items WHERE id = :id LIMIT 1",
        {"id": item_id},
        Item,
    )


async def get_items(shop: str) -> list[Item]:
    return await db.fetchall(
        "SELECT * FROM offlineshop.items WHERE shop = :shop",
        {"shop": shop},
        Item,
    )


async def delete_item_from_shop(shop: str, item_id: str):
    await db.execute(
        """
        DELETE FROM offlineshop.items WHERE shop = :shop AND id = :id
        """,
        {"shop": shop, "id": item_id},
    )
