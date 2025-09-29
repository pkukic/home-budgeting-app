from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# User schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True


# Category schemas
class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True


# Expense schemas
class ExpenseBase(BaseModel):
    amount: float
    description: Optional[str] = None
    category_id: int


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseResponse(ExpenseBase):
    id: int
    date: datetime
    owner_id: int
    category: CategoryResponse
    
    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str