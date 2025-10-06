from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from database import get_db
from models import Product
from schemas import ProductIn, ProductOut
from deps import get_current_user

router = APIRouter(prefix="/api/products", tags=["products"])


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    exists = db.query(Product).filter(Product.sku == payload.sku).first()
    if exists:
        raise HTTPException(status_code=400, detail="SKU already exists")

    product = Product(
        name=payload.name,
        slug=payload.slug,
        sku=payload.sku,
        price=payload.price,
        qty_in_stock=payload.qty_in_stock,
        is_active=payload.is_active,
    )

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/", response_model=List[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or SKU"),
    ordering: Optional[str] = Query(None, description="Order by field, e.g. price or -price"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
):
    query = db.query(Product)

    # Search
    if search:
        query = query.filter(or_(Product.name.ilike(f"%{search}%"), Product.sku.ilike(f"%{search}%")))

    # Ordering
    if ordering:
        order_field = ordering.lstrip("-")
        if hasattr(Product, order_field):
            column = getattr(Product, order_field)
            if ordering.startswith("-"):
                column = column.desc()
            query = query.order_by(column)

    # Pagination
    total = query.count()
    products = query.offset((page - 1) * page_size).limit(page_size).all()

    return products


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = payload.name
    product.slug = payload.slug
    product.sku = payload.sku
    product.price = payload.price
    product.qty_in_stock = payload.qty_in_stock
    product.is_active = payload.is_active

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return None
