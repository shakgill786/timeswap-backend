from pydantic import BaseModel, EmailStr
from typing import Optional

### 🚀 User Schemas ###
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

### 🚀 Product Schemas ###
class ProductBase(BaseModel):
    title: str
    description: str
    category: str
    image: Optional[str] = None
    barter_options: str

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

### 🚀 Review Schemas ###
class ReviewBase(BaseModel):
    rating: float
    comment: str

class ReviewCreate(ReviewBase):
    product_id: int

class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    product_id: int

    class Config:
        from_attributes = True
