from .connection import db_pool


async def create_db():
    pool = await db_pool()

    async with pool.acquire() as connection:
        await connection.execute("DROP TABLE IF EXISTS inventory CASCADE")

        query = """
                CREATE TABLE inventory(
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER NOT NULL,
                    count INTEGER NOT NULL,
                    UNIQUE (product_id, count),
                    CONSTRAINT positive_count CHECK (count >= 0)
                )
                """
        await connection.execute(query)

        query = """
            INSERT INTO inventory (product_id, count) VALUES ($1, $2)
            """
        data = (
            (1, 44),
            (2, 20),
            (3, 132),
            (4, 75),
        )

        await connection.executemany(query, args=data)
