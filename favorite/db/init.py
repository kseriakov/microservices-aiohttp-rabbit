from .connection import db_pool


async def create_db():
    pool = await db_pool()

    async with pool.acquire() as connection:
        await connection.execute("DROP TABLE IF EXISTS favorite CASCADE")

        query = """
                CREATE TABLE favorite(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    UNIQUE (user_id, product_id)
                )
                """
        await connection.execute(query)

        query = """
            INSERT INTO favorite (user_id, product_id) VALUES ($1, $2)
            """
        data = (
            (1, 3),
            (1, 2),
            (2, 2),
            (2, 4),
        )

        await connection.executemany(query, args=data)
