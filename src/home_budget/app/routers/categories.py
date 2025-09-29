from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from home_budget.app.database import get_db
from home_budget.app.schemas import CategoryCreate, CategoryResponse
from home_budget.app.crud import CategoryCRUD

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    # Check if category already exists
    if CategoryCRUD.exists_by_name(db, category.name):
        raise HTTPException(status_code=400, detail="Category already exists")
    
    # Create new category
    return CategoryCRUD.create(db, category)


@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    return CategoryCRUD.get_all(db)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID"""
    category = CategoryCRUD.get_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    """Update a category"""
    # Check if category exists
    if not CategoryCRUD.get_by_id(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if new name already exists (excluding current category)
    if CategoryCRUD.exists_by_name(db, category.name, exclude_id=category_id):
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    # Update category
    updated_category = CategoryCRUD.update(db, category_id, category)
    return updated_category


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category"""
    if not CategoryCRUD.delete(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"message": "Category deleted successfully"}