from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from typing import List

from models import Order, Product, User, Customer, OrderItem
from schemas import OrderCreate, OrderOut
from deps import get_db, get_current_user

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    if product.qty_in_stock < payload.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")


    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        customer = Customer(
            user_id=current_user.id,
            full_name=current_user.email.split("@")[0].title(),
            email=current_user.email
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    total_price = product.price * payload.quantity

    order = Order(
        user_id=current_user.id,
        customer_id=customer.id,
        total=total_price,
    )
    db.add(order)
    db.flush()


    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        qty=payload.quantity,
        unit_price=product.price,
        line_total=total_price
    )
    db.add(order_item)

    product.qty_in_stock -= payload.quantity

    db.commit()


    final_order = db.query(Order).options(
        selectinload(Order.items)
    ).filter(Order.id == order.id).first()

    return final_order


@router.get("/", response_model=List[OrderOut])
def list_orders(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    # İlişkili öğeleri (items) her zaman yükle
    query = db.query(Order).options(selectinload(Order.items))

    if current_user.role.value == "admin":
        orders = query.all()
    else:
        orders = query.filter(Order.user_id == current_user.id).all()

    return orders


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int,
              db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    order = db.query(Order).options(
        selectinload(Order.items)
    ).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this order")

    return order


@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: int,
                 payload: OrderCreate,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    order = db.query(Order).options(selectinload(Order.items)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if order.status.value != "NEW":
        raise HTTPException(status_code=400, detail="Only NEW orders can be updated")

    for item in order.items:
        product_old = db.query(Product).filter(Product.id == item.product_id).first()
        if product_old:
            product_old.qty_in_stock += item.qty
        db.delete(item)

    db.commit()

    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.qty_in_stock < payload.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    order_item = OrderItem(
        order_id=order.id,
        product_id=payload.product_id,
        qty=payload.quantity,
        unit_price=product.price,
        line_total=product.price * payload.quantity
    )
    db.add(order_item)

    product.qty_in_stock -= payload.quantity
    order.total = product.price * payload.quantity

    db.commit()
    db.refresh(order)

    final_order = db.query(Order).options(selectinload(Order.items)).filter(Order.id == order.id).first()
    return final_order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if order.status.value != "NEW":
        raise HTTPException(status_code=400, detail="Cannot delete non-NEW orders")

    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.qty_in_stock += item.qty

    db.delete(order)
    db.commit()
    return None