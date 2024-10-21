import time
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from lnbits.core.crud import get_standalone_payment
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

from .crud import get_item, get_shop

offlineshop_generic_router = APIRouter()


def offlineshop_renderer():
    return template_renderer(["offlineshop/templates"])


@offlineshop_generic_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return offlineshop_renderer().TemplateResponse(
        "offlineshop/index.html", {"request": request, "user": user.json()}
    )


@offlineshop_generic_router.get("/print", response_class=HTMLResponse)
async def print_qr_codes(request: Request):
    items = []
    for item_id in request.query_params.get("items", "").split(","):
        item = await get_item(item_id)
        if item:
            items.append(
                {
                    "lnurl": item.lnurl(request),
                    "name": item.name,
                    "price": f"{round(item.price, 2) if item.unit != 'sats' else int(item.price)} {item.unit}",
                }
            )

    return offlineshop_renderer().TemplateResponse(
        "offlineshop/print.html",
        {"request": request, "items": items},
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
        {payment.time.strftime('%Y-%m-%d %H:%M:%S')}
        {style}
        """
