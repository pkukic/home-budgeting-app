from sqlalchemy.orm import Session
from typing import Optional, List
from home_budget.app.models import Category, User, Expense
from home_budget.app.schemas import CategoryCreate, UserCreate, ExpenseCreate


class CategoryCRUD:
    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return db.query(Category).filter(Category.id == category_id).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Category]:
        """Get category by name"""
        return db.query(Category).filter(Category.name == name).first()
    
    @staticmethod
    def get_all(db: Session) -> List[Category]:
        """Get all categories"""
        return db.query(Category).all()
    
    @staticmethod
    def create(db: Session, category: CategoryCreate) -> Category:
        """Create a new category"""
        db_category = Category(name=category.name)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def update(db: Session, category_id: int, category: CategoryCreate) -> Optional[Category]:
        """Update a category"""
        db_category = CategoryCRUD.get_by_id(db, category_id)
        if db_category:
            db_category.name = category.name
            db.commit()
            db.refresh(db_category)
        return db_category
    
    @staticmethod
    def delete(db: Session, category_id: int) -> bool:
        """Delete a category"""
        db_category = CategoryCRUD.get_by_id(db, category_id)
        if db_category:
            db.delete(db_category)
            db.commit()
            return True
        return False
    
    @staticmethod
    def exists_by_name(db: Session, name: str, exclude_id: Optional[int] = None) -> bool:
        """Check if category name already exists, optionally excluding a specific ID"""
        query = db.query(Category).filter(Category.name == name)
        if exclude_id:
            query = query.filter(Category.id != exclude_id)
        return query.first() is not None


class UserCRUD:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create(db: Session, user: UserCreate, hashed_password: str) -> User:
        """Create a new user"""
        db_user = User(email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


class ExpenseCRUD:
    @staticmethod
    def get_by_id(db: Session, expense_id: int) -> Optional[Expense]:
        """Get expense by ID"""
        return db.query(Expense).filter(Expense.id == expense_id).first()
    
    @staticmethod
    def get_by_user(db: Session, user_id: int) -> List[Expense]:
        """Get all expenses for a user"""
        return db.query(Expense).filter(Expense.owner_id == user_id).all()
    
    @staticmethod
    def create(db: Session, expense: ExpenseCreate, user_id: int) -> Expense:
        """Create a new expense"""
        db_expense = Expense(
            amount=expense.amount,
            description=expense.description,
            category_id=expense.category_id,
            owner_id=user_id
        )
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return db_expense