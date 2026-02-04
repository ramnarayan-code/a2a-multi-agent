from pydantic import BaseModel
from typing import List, Optional

class Product(BaseModel):
    product_id: str
    name: str
    description: str
    price: float
    stock: int
    category: str

class CartItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    subtotal: float

class Cart(BaseModel):
    items: List[CartItem]
    total: float
    item_count: int

class Order(BaseModel):
    order_id: str
    items: List[CartItem]
    total: float
    payment_method: str
    status: str
    created_at: str
    updated_at: str
    tracking_number: Optional[str] = None
