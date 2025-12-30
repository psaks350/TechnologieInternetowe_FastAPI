from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

# KUPONY
class Coupon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    discount_percent: int
    is_active: bool = True

# PRODUKTY
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float 

# KOSZYK
class CartItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    qty: int = Field(default=1)
    product: Product = Relationship()

# ZAMÓWIENIA
class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Pola do zapisu rabatu
    coupon_code: Optional[str] = None
    discount_amount: float = 0.0
    final_total: float = 0.0

    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    qty: int
    price: float 
    
    order: Order = Relationship(back_populates="items")
    product: Product = Relationship()

# MODELE API

class ProductCreate(SQLModel):
    name: str
    price: float

class CartAdd(SQLModel):
    product_id: int
    qty: int = 1

class CartUpdate(SQLModel):
    qty: int

class CartRead(SQLModel):
    id: int
    qty: int
    product: Product

class CheckoutRequest(SQLModel):
    coupon_code: Optional[str] = None

class CouponCreate(SQLModel):
    code: str
    discount_percent: int

class OrderRead(SQLModel):
    id: int
    created_at: datetime
    coupon_code: Optional[str]
    discount_amount: float
    final_total: float
    items: List["OrderItem"]

class OrderItemRead(SQLModel):
    qty: int
    price: float
    product: Product

class OrderRead(SQLModel):
    id: int
    created_at: datetime
    coupon_code: Optional[str] = None
    discount_amount: float
    final_total: float
    items: List[OrderItemRead]