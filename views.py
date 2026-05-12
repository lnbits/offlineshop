import time
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from lnbits.core.crud import get_standalone_payment
from lnbits.core.views.generic import index, index_public
from lnbits.decorators import check_user_exists

from .crud import get_item, get_shop

offlineshop_generic_router = APIRouter()


offlineshop_generic_router.add_api_route(
    "/", methods=["GET"], endpoint=index, dependencies=[Depends(check_user_exists)]
)

offlineshop_generic_router.add_api_route(
    "/print", methods=["GET"], endpoint=index_public
)


@offlineshop_generic_router.get(
    "/confirmation/{p}",
    name="offlineshop.confirmation_code",
    response_class=HTMLResponse,
)
async def confirmation_code(p: str):
    style = "<style>* { font-size: 100px}</style>"

    payment_hash = p
    payment = await get_standalone_payment(payment_hash, incoming=True)
    if not payment:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Couldn't find the payment {payment_hash}." + style,
        )
    if payment.pending:
        raise HTTPException(
            status_code=HTTPStatus.PAYMENT_REQUIRED,
            detail=f"Payment {payment_hash} wasn't received yet. Try again in a minute."
            + style,
        )

    if payment.time.timestamp() + 60 * 15 < time.time():
        raise HTTPException(
            status_code=HTTPStatus.REQUEST_TIMEOUT,
            detail="Too much time has passed." + style,
        )

    if not payment.extra or not payment.extra.get("item"):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Payment is missing extra data."
        )

    assert payment.extra
    item_id = payment.extra.get("item")
    assert item_id
    item = await get_item(item_id)
    assert item
    shop = await get_shop(item.shop)
    assert shop

    return f"""
        [{shop.get_code(payment_hash)}]<br>
        {item.name}<br>
        {item.price} {item.unit}<br>
        {payment.time.strftime("%Y-%m-%d %H:%M:%S")}
        {style}
        """
