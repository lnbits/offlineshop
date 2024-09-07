import base64
import hashlib
import json
from collections import OrderedDict
from typing import Optional

from fastapi import Query
from lnurl import encode as lnurl_encode
from lnurl.types import LnurlPayMetadata
from pydantic import BaseModel
from starlette.requests import Request

from .helpers import totp

shop_counters: dict = {}


class ShopCounter:
    wordlist: list[str]
    fulfilled_payments: OrderedDict
    counter: int

    @classmethod
    def invoke(cls, shop: "Shop"):
        shop_counter = shop_counters.get(shop.id)
        if not shop_counter:
            shop_counter = cls(wordlist=shop.wordlist.split("\n"))
            shop_counters[shop.id] = shop_counter
        return shop_counter

    @classmethod
    def reset(cls, shop: "Shop"):
        shop_counter = cls.invoke(shop)
        shop_counter.counter = -1
        shop_counter.wordlist = shop.wordlist.split("\n")

    def __init__(self, wordlist: list[str]):
        self.wordlist = wordlist
        self.fulfilled_payments = OrderedDict()
        self.counter = -1

    def get_word(self, payment_hash):
        if payment_hash in self.fulfilled_payments:
            return self.fulfilled_payments[payment_hash]

        # get a new word
        self.counter += 1
        word = self.wordlist[self.counter % len(self.wordlist)]
        self.fulfilled_payments[payment_hash] = word

        # cleanup confirmation words cache
        to_remove = len(self.fulfilled_payments) - 23
        if to_remove > 0:
            for _ in range(to_remove):
                self.fulfilled_payments.popitem(False)

        return word


class CreateShop(BaseModel):
    wallet: str
    method: Optional[str] = "wordlist"
    wordlist: Optional[str] = None


class Shop(BaseModel):
    id: str
    wallet: str
    method: str
    wordlist: str

    @property
    def otp_key(self) -> str:
        return base64.b32encode(
            hashlib.sha256(
                ("otpkey" + str(self.id) + self.wallet).encode("ascii")
            ).digest()
        ).decode("ascii")

    def get_code(self, payment_hash: str) -> str:
        if self.method == "wordlist":
            sc = ShopCounter.invoke(self)
            return sc.get_word(payment_hash)
        elif self.method == "totp":
            return totp(self.otp_key)
        return ""


class Item(BaseModel):
    shop: str
    id: str
    name: str
    description: str
    image: Optional[str]
    enabled: bool
    price: float
    unit: str
    fiat_base_multiplier: int

    def lnurl(self, req: Request) -> str:
        return lnurl_encode(
            str(req.url_for("offlineshop.lnurl_response", item_id=self.id))
        )

    def values(self, req: Request):
        values = self.dict()
        values["lnurl"] = lnurl_encode(
            str(req.url_for("offlineshop.lnurl_response", item_id=self.id))
        )
        return values

    async def lnurlpay_metadata(self) -> LnurlPayMetadata:
        metadata = [["text/plain", self.description]]

        if self.image:
            metadata.append(self.image.split(":")[1].split(","))

        return LnurlPayMetadata(json.dumps(metadata))


class CreateItem(BaseModel):
    name: str
    description: str
    price: float
    unit: str
    fiat_base_multiplier: int = Query(100, ge=1)
    image: Optional[str] = None
