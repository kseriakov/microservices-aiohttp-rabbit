from .connection import db_pool


async def create_db():
    pool = await db_pool()

    async with pool.acquire() as connection:
        await connection.execute("DROP TABLE IF EXISTS products CASCADE")

        query = """
                CREATE TABLE products(
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    price NUMERIC(5, 2) NOT NULL,
                    CONSTRAINT positive_price CHECK (price > 0)
                )
                """
        await connection.execute(query)

        query = """
            INSERT INTO products (name, price) VALUES ($1, $2)
            """
        data = (
            ("book", "123.31"),
            ("table", "575.20"),
            ("pen", "30.33"),
            ("clock", "200.50"),
        )

        await connection.executemany(query, args=data)
