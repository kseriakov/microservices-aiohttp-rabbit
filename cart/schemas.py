from pydantic import BaseModel


class BaseCartProduct(BaseModel):
    user_id: int
    product_id: int


class CreateCartProduct(BaseCartProduct):
    ...


class DeleteCartProduct(BaseCartProduct):
    ...


class ShowCartProducts(BaseModel):
    user_id: int
    cart_products: list[int]
