from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from database import get_db
from models import Customer, User
from schemas import CustomerOut
from deps import get_current_user
from fastapi import Body

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("/", response_model=List[CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or email"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    user: User = Depends(get_current_user),
):
    # Sadece admin customers görebilir
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    query = db.query(Customer)

    if search:
        query = query.filter(
            or_(
                Customer.full_name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%")
            )
        )

    customers = query.offset((page - 1) * page_size).limit(page_size).all()
    return customers


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/", response_model=CustomerOut, status_code=201)
def create_customer_auto(
    email: str = Body(...),
    db: Session = Depends(get_db),
):
    existing = db.query(Customer).filter(Customer.email == email).first()
    if existing:
        return existing

    customer = Customer(email=email)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer
