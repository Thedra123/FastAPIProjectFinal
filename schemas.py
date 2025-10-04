from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    user = "user"

class UserBase(BaseModel):
    email: EmailStr

class UserRegister(UserBase):
    password: str
    role: Optional[Role] = Role.user

class UserLogin(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    role: Role
    is_active: bool
    class Config:
        orm_mode = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str

# ---------- PRODUCT SCHEMAS ----------

class ProductBase(BaseModel):
    name: str
    slug: str
    sku: str
    price: float
    qty_in_stock: int
    is_active: bool = True

class ProductIn(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int

    class Config:
        orm_mode = True


# ---------- CUSTOMER SCHEMAS ----------

class CustomerBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None

class CustomerIn(CustomerBase):
    pass

class CustomerOut(CustomerBase):
    id: int

    class Config:
        orm_mode = True


# ---------- ORDER SCHEMAS (single product) ----------

from enum import Enum as PyEnum

class OrderStatus(str, PyEnum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    canceled = "canceled"

class OrderBase(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int
    user_id: int
    total_price: float
    status: OrderStatus

    class Config:
        orm_mode = True



