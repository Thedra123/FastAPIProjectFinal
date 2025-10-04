from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import Order, Product, User
from schemas import OrderCreate, OrderOut
from deps import get_db, get_current_user

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    """
    Create a new order for the current user.
    """
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    total_price = product.price * payload.quantity

    order = Order(
        user_id=current_user.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        total_price=total_price,
        status="pending"
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/", response_model=List[OrderOut])
def list_orders(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    """
    List all orders belonging to the current user.
    Admins can see all orders.
    """
    if current_user.role.value == "admin":
        orders = db.query(Order).all()
    else:
        orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int,
              db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    """
    Get details of a specific order.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
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
    """
    Update an order (quantity or product). Only pending orders.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending orders can be updated")

    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    order.product_id = payload.product_id
    order.quantity = payload.quantity
    order.total_price = product.price * payload.quantity

    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    """
    Delete an order (only pending ones).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Cannot delete non-pending orders")

    db.delete(order)
    db.commit()
    return None
