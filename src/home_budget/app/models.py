from sqlalchemy import (
    Column, 
    Integer, 
    String,
    Float, 
    ForeignKey, 
    DateTime
)
from sqlalchemy.orm import relationship
from home_budget.app.database import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # A user can have multiple expenses
    # Each expense has a single owner    
    expenses = relationship("Expense", back_populates="owner")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.now(timezone.utc))
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # This is where we define the owner relationship
    owner = relationship("User", back_populates="expenses")
    category = relationship("Category")