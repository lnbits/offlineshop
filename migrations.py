async def m001_initial(db):
    """
    Initial offlineshop tables.
    """
    await db.execute(
        f"""
        CREATE TABLE offlineshop.shops (
            id {db.serial_primary_key},
            wallet TEXT NOT NULL,
            method TEXT NOT NULL,
            wordlist TEXT
        );
        """
    )

    await db.execute(
        f"""
        CREATE TABLE offlineshop.items (
            shop INTEGER NOT NULL REFERENCES {db.references_schema}shops (id),
            id {db.serial_primary_key},
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            image TEXT, -- image/png;base64,...
            enabled BOOLEAN NOT NULL DEFAULT true,
            price {db.big_int} NOT NULL,
            unit TEXT NOT NULL DEFAULT 'sat'
        );
        """
    )


async def m002_fiat_base_multiplier(db):
    """
    Store the multiplier for fiat prices. We store the price in cents and
    remember to multiply by 100 when we use it to convert to Dollars.
    """
    await db.execute(
        """
        ALTER TABLE offlineshop.items ADD COLUMN fiat_base_multiplier INTEGER DEFAULT 1
        """
    )


async def m003_id_as_text(db):
    """
    Change the id columns to TEXT.
    """
    # Shops
    await db.execute("ALTER TABLE offlineshop.shops RENAME TO old_shop;")
    await db.execute(
        """
        CREATE TABLE offlineshop.shops (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            method TEXT NOT NULL,
            wordlist TEXT
        );
    """
    )
    await db.execute(
        """
        INSERT INTO offlineshop.shops (id, wallet, method, wordlist)
        SELECT id, wallet, method, wordlist FROM offlineshop.old_shop;
    """
    )

    # Items
    await db.execute("UPDATE offlineshop.items SET unit = 'sats' WHERE unit = 'sat';")
    await db.execute("ALTER TABLE offlineshop.items RENAME TO old_item;")
    await db.execute(
        """
        CREATE TABLE offlineshop.items (
            shop TEXT NOT NULL,
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            image TEXT,
            enabled BOOLEAN NOT NULL DEFAULT true,
            price REAL NOT NULL,
            unit TEXT NOT NULL DEFAULT 'sats'
        );
    """
    )
    await db.execute(
        """
        INSERT INTO offlineshop.items
        (shop, id, name, description, image, enabled, price, unit)
        SELECT shop, id, name, description, image, enabled, price, unit FROM
        offlineshop.old_item;
    """
    )
    await db.execute(
        "UPDATE offlineshop.items SET price = price / 100 WHERE unit != 'sats';"
    )
    await db.execute("DROP TABLE offlineshop.old_item;")
    await db.execute("DROP TABLE offlineshop.old_shop;")
