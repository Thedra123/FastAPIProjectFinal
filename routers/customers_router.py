from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from database import get_db
from models import Customer
from schemas import CustomerIn, CustomerOut
from deps import get_current_user

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.post("/", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    exists = db.query(Customer).filter(Customer.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already exists")

    customer = Customer(full_name=payload.full_name, email=payload.email, phone=payload.phone)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/", response_model=List[CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or email"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
):
    query = db.query(Customer)

    if search:
        query = query.filter(or_(Customer.full_name.ilike(f"%{search}%"), Customer.email.ilike(f"%{search}%")))

    total = query.count()
    customers = query.offset((page - 1) * page_size).limit(page_size).all()

    return customers


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    payload: CustomerIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.full_name = payload.full_name
    customer.email = payload.email
    customer.phone = payload.phone

    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()
    return None
