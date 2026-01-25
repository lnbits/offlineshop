<a href="https://lnbits.com" target="_blank" rel="noopener noreferrer">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://i.imgur.com/QE6SIrs.png">
    <img src="https://i.imgur.com/fyKPgVT.png" alt="LNbits" style="width:280px">
  </picture>
</a>

[![License: MIT](https://img.shields.io/badge/License-MIT-success?logo=open-source-initiative&logoColor=white)](./LICENSE)
[![Built for LNbits](https://img.shields.io/badge/Built%20for-LNbits-4D4DFF?logo=lightning&logoColor=white)](https://github.com/lnbits/lnbits)

# Offline Shop - <small>[LNbits](https://github.com/lnbits/lnbits) extension</small>

<small>For more about LNBits extension check [this tutorial](https://github.com/lnbits/lnbits/wiki/LNbits-Extensions)</small>

## Create QR codes for each product and display them on your store for receiving payments Offline

[![video tutorial offline shop](http://img.youtube.com/vi/_XAvM_LNsoo/0.jpg)](https://youtu.be/_XAvM_LNsoo 'video tutorial offline shop')

LNbits Offline Shop allows for merchants to receive Bitcoin payments while offline and without any electronic device.

Merchant will create items and associate a QR code ([a LNURLp](https://github.com/lnbits/lnbits/blob/master/lnbits/extensions/lnurlp/README.md)) with a price. He can then print the QR codes and display them on their shop. When a customer chooses an item, scans the QR code, gets the description and price. After payment, the customer gets a confirmation code that the merchant can validate to be sure the payment was successful.

Customers must use an LNURL pay capable wallet.

[**Wallets supporting LNURL**](https://github.com/fiatjaf/awesome-lnurl#wallets)

## Usage

1. Entering the Offline shop extension you'll see an Items list, the Shop wallet and a Wordslist\
   ![offline shop back office](https://i.imgur.com/Ei7cxj9.png)
2. Begin by creating an item, click "ADD NEW ITEM"
   - set the item name and a small description
   - you can set an optional, preferably square image, that will show up on the customer wallet - _depending on wallet_
   - set the item price, if you choose a fiat currency the bitcoin conversion will happen at the time customer scans to pay\
     ![add new item](https://i.imgur.com/pkZqRgj.png)
3. After creating some products, click on "PRINT QR CODES"\
   ![print qr codes](https://i.imgur.com/2GAiSTe.png)
4. You'll see a QR code for each product in your LNbits Offline Shop with a title and price ready for printing\
   ![qr codes sheet](https://i.imgur.com/faEqOcd.png)
5. Place the printed QR codes on your shop, or at the fair stall, or have them as a menu style laminated sheet
6. Choose what type of confirmation do you want customers to report to merchant after a successful payment\
   ![wordlist](https://i.imgur.com/9aM6NUL.png)

   - Wordlist is the default option: after a successful payment the customer will receive a word from this list, **sequentially**. Starting in _albatross_ as customers pay for the items they will get the next word in the list until _zebra_, then it starts at the top again. The list can be changed, for example if you think A-Z is a big list to track, you can use _apple_, _banana_, _coconut_\
     ![totp authenticator](https://i.imgur.com/MrJXFxz.png)
   - TOTP (time-based one time password) can be used instead. If you use Google Authenticator just scan the presented QR with the app and after a successful payment the user will get the password that you can check with GA\
     ![disable confirmations](https://i.imgur.com/2OFs4yi.png)
   - Nothing, disables the need for confirmation of payment, click the "DISABLE CONFIRMATION CODES"

## Powered by LNbits

[LNbits](https://lnbits.com) is a free and open-source lightning accounts system.

[![Visit LNbits Shop](https://img.shields.io/badge/Visit-LNbits%20Shop-7C3AED?logo=shopping-cart&logoColor=white&labelColor=5B21B6)](https://shop.lnbits.com/)
[![Try myLNbits SaaS](https://img.shields.io/badge/Try-myLNbits%20SaaS-2563EB?logo=lightning&logoColor=white&labelColor=1E40AF)](https://my.lnbits.com/login)
