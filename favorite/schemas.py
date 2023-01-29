from pydantic import BaseModel


class BaseFavoriteProduct(BaseModel):
    user_id: int
    product_id: int


class CreateFavoriteProduct(BaseFavoriteProduct):
    ...

class DeleteFavoriteProduct(BaseFavoriteProduct):
    ...


class ShowFavoriteProducts(BaseModel):
    user_id: int
    favorite_products: list[int]
