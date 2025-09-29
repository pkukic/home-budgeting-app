from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


# User schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")

    @field_validator('password')
    def validate_password(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Password cannot be empty')
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserResponse(UserBase):
    id: int
    balance: float
    
    class Config:
        from_attributes = True


# Category schemas
class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    name: str = Field(..., min_length=1, description="Category name is required and cannot be empty")
    
    @field_validator('name')
    def validate_name(cls, v):
        if not v:
            raise ValueError('Category name cannot be empty')
        stripped = v.strip()
        if len(stripped) == 0:
            raise ValueError('Category name cannot be only whitespace')
        return stripped

class CategoryResponse(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True


# Expense schemas
class ExpenseBase(BaseModel):
    amount: float
    description: str
    category_id: int


class ExpenseCreate(ExpenseBase):
    amount: float = Field(..., gt=0, description="Expense amount must be positive")
    description: str = Field(..., description="Description of the expense")
    category_id: int = Field(..., gt=0, description="Category ID must be positive")

    @field_validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Expense amount must be positive')
        return v
    
    @field_validator('description')
    def validate_description(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Description cannot be empty')
        return v.strip()
    
    @field_validator('category_id')
    def validate_category_id(cls, v):   
        if v <= 0:
            raise ValueError('Category ID must be positive')
        return v

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
    password: str = Field(..., min_length=1, description="Password is required")
    
    @field_validator('password')
    def validate_password(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Password cannot be empty')
        return v