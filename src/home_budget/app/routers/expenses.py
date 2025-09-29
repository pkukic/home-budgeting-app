from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from home_budget.app.database import get_db
from home_budget.app.schemas import ExpenseCreate, ExpenseResponse
from home_budget.app.crud import ExpenseCRUD, CategoryCRUD, UserCRUD
from home_budget.app.dependencies import get_current_user_dependency
from home_budget.app.models import User

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/", response_model=ExpenseResponse)
def create_expense(
    expense: ExpenseCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Create a new expense for the authenticated user"""
    
    # Validate that the category exists
    category = CategoryCRUD.get_by_id(db, expense.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Validate amount is positive
    if expense.amount <= 0:
        raise HTTPException(status_code=400, detail="Expense amount must be positive")
    
    # Check if user has sufficient balance
    if current_user.balance < expense.amount:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient balance. Current balance: {current_user.balance}, Required: {expense.amount}"
        )
    
    # Create the expense
    db_expense = ExpenseCRUD.create(db, expense, current_user.id)
    
    # Deduct amount from user's balance
    current_user.balance -= expense.amount
    db.commit()
    db.refresh(current_user)
    
    return db_expense


@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    min_amount: Optional[float] = Query(None, description="Filter by minimum amount"),
    max_amount: Optional[float] = Query(None, description="Filter by maximum amount")
):
    """Get all expenses for the authenticated user with optional filters"""
    
    # Get user's expenses
    expenses = ExpenseCRUD.get_by_user(db, current_user.id)
    
    # Apply filters if provided
    if category_id:
        expenses = [exp for exp in expenses if exp.category_id == category_id]
    
    if min_amount is not None:
        expenses = [exp for exp in expenses if exp.amount >= min_amount]
    
    if max_amount is not None:
        expenses = [exp for exp in expenses if exp.amount <= max_amount]
    
    return expenses


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get a specific expense by ID (only if owned by the authenticated user)"""
    
    expense = ExpenseCRUD.get_by_id(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Check if the expense belongs to the current user
    if expense.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this expense")
    
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_update: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Update an expense (only if owned by the authenticated user)"""
    
    # Get the existing expense
    db_expense = ExpenseCRUD.get_by_id(db, expense_id)
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Check ownership
    if db_expense.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this expense")
    
    # Validate category exists
    category = CategoryCRUD.get_by_id(db, expense_update.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Validate amount is positive
    if expense_update.amount <= 0:
        raise HTTPException(status_code=400, detail="Expense amount must be positive")
    
    # Calculate balance adjustment
    old_amount = db_expense.amount
    new_amount = expense_update.amount
    balance_difference = new_amount - old_amount
    
    # Check if user has sufficient balance for the increase
    if balance_difference > 0 and current_user.balance < balance_difference:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance for update. Current balance: {current_user.balance}, Additional required: {balance_difference}"
        )
    
    # Update the expense
    db_expense.amount = expense_update.amount
    db_expense.description = expense_update.description
    db_expense.category_id = expense_update.category_id
    
    # Adjust user's balance
    current_user.balance -= balance_difference
    
    db.commit()
    db.refresh(db_expense)
    db.refresh(current_user)
    
    return db_expense


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Delete an expense (only if owned by the authenticated user)"""
    
    # Get the expense
    db_expense = ExpenseCRUD.get_by_id(db, expense_id)
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Check ownership
    if db_expense.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this expense")
    
    # Store the amount to refund
    refund_amount = db_expense.amount
    
    # Delete the expense
    ExpenseCRUD.delete(db, expense_id)
    
    # Refund the amount to user's balance
    current_user.balance += refund_amount
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Expense deleted successfully", "refunded_amount": refund_amount}


@router.get("/stats/summary")
def get_expense_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get expense summary for the authenticated user"""
    
    expenses = ExpenseCRUD.get_by_user(db, current_user.id)
    
    total_expenses = sum(exp.amount for exp in expenses)
    expense_count = len(expenses)
    
    # Group by category
    category_totals = {}
    for expense in expenses:
        category_name = expense.category.name
        if category_name not in category_totals:
            category_totals[category_name] = 0
        category_totals[category_name] += expense.amount
    
    return {
        "total_expenses": total_expenses,
        "expense_count": expense_count,
        "remaining_balance": current_user.balance,
        "category_breakdown": category_totals
    }