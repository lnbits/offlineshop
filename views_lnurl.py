from typing import Union

from fastapi import APIRouter
from lnbits.core.services import create_invoice
from lnbits.utils.exchange_rates import fiat_amount_as_satoshis
from lnurl import LnurlErrorResponse, LnurlPayActionResponse, LnurlPayResponse
from lnurl.models import UrlAction
from lnurl.types import (
    ClearnetUrl,
    DebugUrl,
    LightningInvoice,
    Max144Str,
    MilliSatoshi,
    OnionUrl,
)
from pydantic import parse_obj_as
from starlette.requests import Request

from .crud import get_item, get_shop

offlineshop_lnurl_router = APIRouter()


@offlineshop_lnurl_router.get("/lnurl/{item_id}", name="offlineshop.lnurl_response")
async def lnurl_response(req: Request, item_id: str) -> dict:
    item = await get_item(item_id)
    if not item:
        return {"status": "ERROR", "reason": "Item not found."}

    if not item.enabled:
        return {"status": "ERROR", "reason": "Item disabled."}

    price_msat = (
        await fiat_amount_as_satoshis(item.price, item.unit)
        if item.unit != "sat"
        else item.price
    ) * 1000

    url = parse_obj_as(
        Union[DebugUrl, OnionUrl, ClearnetUrl],  # type: ignore
        str(req.url_for("offlineshop.lnurl_callback", item_id=item.id)),
    )

    resp = LnurlPayResponse(
        callback=url,
        minSendable=MilliSatoshi(price_msat),
        maxSendable=MilliSatoshi(price_msat),
        metadata=await item.lnurlpay_metadata(),
    )

    return resp.dict()


@offlineshop_lnurl_router.get("/lnurl/cb/{item_id}", name="offlineshop.lnurl_callback")
async def lnurl_callback(request: Request, item_id: str):
    item = await get_item(item_id)
    if not item:
        return {"status": "ERROR", "reason": "Couldn't find item."}

    if item.unit == "sat":
        min_price = item.price * 1000
        max_price = item.price * 1000
    else:
        price = await fiat_amount_as_satoshis(item.price, item.unit)
        # allow some fluctuation (the fiat price may have changed between the calls)
        min_price = price * 995
        max_price = price * 1010

    amount_received = int(request.query_params.get("amount") or 0)
    if amount_received < min_price:
        return LnurlErrorResponse(
            reason=f"Amount {amount_received} is smaller than minimum {min_price}."
        ).dict()
    elif amount_received > max_price:
        return LnurlErrorResponse(
            reason=f"Amount {amount_received} is greater than maximum {max_price}."
        ).dict()

    shop = await get_shop(item.shop)
    assert shop

    try:
        payment_hash, payment_request = await create_invoice(
            wallet_id=shop.wallet,
            amount=int(amount_received / 1000),
            memo=item.name,
            unhashed_description=(await item.lnurlpay_metadata()).encode(),
            extra={"tag": "offlineshop", "item": item.id},
        )
    except Exception as exc:
        return LnurlErrorResponse(reason=str(exc)).dict()

    if shop.method and shop.wordlist:
        url = parse_obj_as(
            Union[DebugUrl, OnionUrl, ClearnetUrl],  # type: ignore
            str(request.url_for("offlineshop.confirmation_code", p=payment_hash)),
        )

        success_action = UrlAction(
            url=url,
            description=Max144Str(
                "Open to get the confirmation code for your purchase."
            ),
        )
        invoice = parse_obj_as(LightningInvoice, LightningInvoice(payment_request))
        resp = LnurlPayActionResponse(
            pr=invoice,
            successAction=success_action,
            routes=[],
        )

        return resp.dict()
