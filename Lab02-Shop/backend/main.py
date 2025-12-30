from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from contextlib import asynccontextmanager

from database import init_db, get_session
from models import (
    Product, ProductCreate,
    CartItem, CartAdd, CartUpdate, CartRead,
    Order, OrderItem, OrderRead, CheckoutRequest,
    Coupon, CouponCreate, OrderItemRead
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Shop API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# PRODUKTY
@app.get("/api/products", response_model=list[Product])
def get_products(db: Session = Depends(get_session)):
    return db.exec(select(Product)).all()

@app.post("/api/products", response_model=Product, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_session)):
    if data.price < 0: raise HTTPException(400, "Cena < 0")
    product = Product.model_validate(data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# KOSZYK
@app.get("/api/cart", response_model=list[CartRead])
def get_cart(db: Session = Depends(get_session)):
    return db.exec(select(CartItem)).all()

@app.post("/api/cart/add", response_model=CartRead)
def add_to_cart(data: CartAdd, db: Session = Depends(get_session)):
    product = db.get(Product, data.product_id)
    if not product: raise HTTPException(404, "Brak produktu")
    if data.qty < 1: raise HTTPException(400, "Ilość < 1")

    existing_item = db.exec(select(CartItem).where(CartItem.product_id == data.product_id)).first()
    if existing_item:
        existing_item.qty += data.qty
        db.add(existing_item)
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        new_item = CartItem(product_id=data.product_id, qty=data.qty)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

@app.patch("/api/cart/item/{product_id}")
def update_cart_item(product_id: int, data: CartUpdate, db: Session = Depends(get_session)):
    item = db.exec(select(CartItem).where(CartItem.product_id == product_id)).first()
    if not item: raise HTTPException(404, "Brak w koszyku")
    
    if data.qty < 1:
        db.delete(item)
        db.commit()
        return {"message": "Usunięto"}
    
    item.qty = data.qty
    db.add(item)
    db.commit()
    return item

@app.delete("/api/cart/item/{product_id}")
def remove_from_cart(product_id: int, db: Session = Depends(get_session)):
    item = db.exec(select(CartItem).where(CartItem.product_id == product_id)).first()
    if item:
        db.delete(item)
        db.commit()
    return {"message": "Usunięto"}

# KUPONY
@app.post("/api/coupons", response_model=Coupon)
def create_coupon(data: CouponCreate, db: Session = Depends(get_session)):

    exists = db.exec(select(Coupon).where(Coupon.code == data.code)).first()
    if exists:
        raise HTTPException(409, "Ten kod już istnieje")
    
    coupon = Coupon.model_validate(data)
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon

@app.get("/api/coupons/{code}", response_model=Coupon)
def verify_coupon(code: str, db: Session = Depends(get_session)):

    coupon = db.exec(select(Coupon).where(Coupon.code == code)).first()
    
    if not coupon:
        raise HTTPException(404, detail="Kod nieprawidłowy")
    
    if not coupon.is_active:
        raise HTTPException(400, detail="Kupon jest nieaktywny")
        
    return coupon


# ZAMÓWIENIA & HISTORIA

@app.get("/api/orders", response_model=list[OrderRead])
def get_orders(db: Session = Depends(get_session)):

    return db.exec(select(Order).order_by(Order.created_at.desc())).all()

@app.post("/api/checkout", response_model=OrderRead, status_code=201)
def checkout(payload: CheckoutRequest, db: Session = Depends(get_session)):

    cart_items = db.exec(select(CartItem)).all()
    if not cart_items: raise HTTPException(400, "Koszyk pusty")

    subtotal = sum(item.product.price * item.qty for item in cart_items)
    discount = 0.0
    used_coupon_code = None

    if payload.coupon_code:
        coupon = db.exec(select(Coupon).where(Coupon.code == payload.coupon_code)).first()
        if not coupon:
            raise HTTPException(404, "Nieprawidłowy kod kuponu")
        if not coupon.is_active:
            raise HTTPException(400, "Kupon nieaktywny")
        
        discount = subtotal * (coupon.discount_percent / 100)
        used_coupon_code = coupon.code

    final_total = subtotal - discount

    new_order = Order(
        coupon_code=used_coupon_code,
        discount_amount=discount,
        final_total=final_total
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            qty=item.qty,
            price=item.product.price
        )
        db.add(order_item)
        db.delete(item)

    db.commit()
    db.refresh(new_order)
    
    return new_order