from fastapi import APIRouter
from lnbits.core.services import create_invoice
from lnbits.utils.exchange_rates import fiat_amount_as_satoshis
from lnurl import (
    CallbackUrl,
    LightningInvoice,
    LnurlErrorResponse,
    LnurlPayActionResponse,
    LnurlPayResponse,
    Max144Str,
    MilliSatoshi,
    UrlAction,
)
from pydantic import parse_obj_as
from starlette.requests import Request

from .crud import get_item, get_shop

offlineshop_lnurl_router = APIRouter()


@offlineshop_lnurl_router.get("/lnurl/{item_id}", name="offlineshop.lnurl_response")
async def lnurl_response(
    req: Request, item_id: str
) -> LnurlPayResponse | LnurlErrorResponse:
    item = await get_item(item_id)
    if not item:
        return LnurlErrorResponse(reason="Item not found.")

    if not item.enabled:
        return LnurlErrorResponse(reason="Item disabled.")

    price_msat = (
        await fiat_amount_as_satoshis(item.price, item.unit)
        if item.unit != "sats"
        else item.price
    ) * 1000

    url = parse_obj_as(
        CallbackUrl,
        str(req.url_for("offlineshop.lnurl_callback", item_id=item.id)),
    )

    return LnurlPayResponse(
        callback=url,
        minSendable=MilliSatoshi(price_msat),
        maxSendable=MilliSatoshi(price_msat),
        metadata=item.lnurlpay_metadata,
    )


@offlineshop_lnurl_router.get("/lnurl/cb/{item_id}", name="offlineshop.lnurl_callback")
async def lnurl_callback(
    request: Request, item_id: str
) -> LnurlPayActionResponse | LnurlErrorResponse:

    item = await get_item(item_id)
    if not item:
        return LnurlErrorResponse(reason="Item not found.")

    if item.unit == "sats":
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
        )
    elif amount_received > max_price:
        return LnurlErrorResponse(
            reason=f"Amount {amount_received} is greater than maximum {max_price}."
        )

    shop = await get_shop(item.shop)
    assert shop

    try:
        payment = await create_invoice(
            wallet_id=shop.wallet,
            amount=int(amount_received / 1000),
            memo=item.name,
            unhashed_description=item.lnurlpay_metadata.encode(),
            extra={"tag": "offlineshop", "item": item.id},
        )
    except Exception as exc:
        return LnurlErrorResponse(reason=str(exc))

    if shop.method and shop.wordlist:
        url = parse_obj_as(
            CallbackUrl,
            str(
                request.url_for("offlineshop.confirmation_code", p=payment.payment_hash)
            ),
        )

        success_action = UrlAction(
            url=url,
            description=Max144Str(
                "Open to get the confirmation code for your purchase."
            ),
        )
        invoice = parse_obj_as(LightningInvoice, LightningInvoice(payment.bolt11))

        return LnurlPayActionResponse(
            pr=invoice,
            successAction=success_action,
        )

    return LnurlErrorResponse(
        reason="Shop does not support confirmation codes."
    )
