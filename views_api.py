from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from lnbits.core.models import WalletTypeInfo
from lnbits.decorators import require_admin_key, require_invoice_key
from lnurl.exceptions import InvalidUrl as LnurlInvalidUrl

from .crud import (
    create_item,
    delete_item_from_shop,
    get_item,
    get_items,
    get_or_create_shop_by_wallet,
    update_item,
    update_shop,
)
from .models import CreateItem, CreateShop, ShopCounter

offlineshop_api_router = APIRouter()


@offlineshop_api_router.get("/api/v1/offlineshop")
async def api_shop_from_wallet(
    r: Request, key_info: WalletTypeInfo = Depends(require_invoice_key)
):
    shop = await get_or_create_shop_by_wallet(key_info.wallet.id)
    assert shop
    items = await get_items(shop.id)

    try:
        return {
            **shop.dict(),
            **{"otp_key": shop.otp_key, "items": [item.values(r) for item in items]},
        }
    except LnurlInvalidUrl as exc:
        raise HTTPException(
            status_code=HTTPStatus.UPGRADE_REQUIRED,
            detail="""
            LNURLs need to be delivered over a
            publically accessible `https` domain or Tor.
            """,
        ) from exc


@offlineshop_api_router.post("/api/v1/offlineshop/items")
@offlineshop_api_router.put("/api/v1/offlineshop/items/{item_id}")
async def api_add_or_update_item(
    data: CreateItem,
    key_info: WalletTypeInfo = Depends(require_admin_key),
    item_id: Optional[str] = None,
):
    shop = await get_or_create_shop_by_wallet(key_info.wallet.id)
    assert shop
    if data.unit == "sats":
        data.price = int(data.price)
    if data.image:
        image_is_url = data.image.startswith("http")
        if not image_is_url:

            def size(b64string):
                return int((len(b64string) * 3) / 4 - b64string.count("=", -2))

            image_size = size(data.image) / 1024
            if image_size > 100:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"""
                    Image size is too big, {int(image_size)}Kb. Max: 100kb,
                    Compress the image at https://tinypng.com, or use an URL.
                    """,
                )
    if item_id is None:
        await create_item(shop.id, data)
        return Response(status_code=HTTPStatus.CREATED)
    else:
        item = await get_item(item_id)
        if not item:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="Item not found"
            )
        for k, v in data.dict().items():
            setattr(item, k, v)
        await update_item(item)


@offlineshop_api_router.delete("/api/v1/offlineshop/items/{item_id}")
async def api_delete_item(
    item_id: str, key_info: WalletTypeInfo = Depends(require_admin_key)
):
    shop = await get_or_create_shop_by_wallet(key_info.wallet.id)
    if not shop:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Shop not found")
    await delete_item_from_shop(shop.id, item_id)


@offlineshop_api_router.put("/api/v1/offlineshop/method")
async def api_update_offlineshop(
    data: CreateShop, key_info: WalletTypeInfo = Depends(require_admin_key)
):
    shop = await get_or_create_shop_by_wallet(key_info.wallet.id)
    if not shop:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    for k, v in data.dict().items():
        setattr(shop, k, v)

    await update_shop(shop)

    ShopCounter.reset(shop)
