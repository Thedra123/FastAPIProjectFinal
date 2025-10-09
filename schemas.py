from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum as PyEnum


# ---------- AUTH SCHEMAS ----------

class Role(str, PyEnum):
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
    # Pydantic V2 Config
    model_config = ConfigDict(from_attributes=True)


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
    # Pydantic V2 Config
    model_config = ConfigDict(from_attributes=True)


# ---------- CUSTOMER SCHEMAS ----------

class CustomerBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None


class CustomerIn(CustomerBase):
    pass


class CustomerOut(CustomerBase):
    id: int
    # Pydantic V2 Config
    model_config = ConfigDict(from_attributes=True)


# ---------- ORDER SCHEMAS ----------

class OrderStatus(str, PyEnum):
    new = "NEW"
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    canceled = "canceled"


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    qty: int
    unit_price: float
    line_total: float
    # Pydantic V2 Config
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    product_id: int
    quantity: int


class OrderOut(BaseModel):
    id: int
    user_id: int
    customer_id: Optional[int] = None

    total: float

    status: OrderStatus
    created_at: datetime

    items: List[OrderItemOut] = []

    # Pydantic V2 Config
    model_config = ConfigDict(from_attributes=True)