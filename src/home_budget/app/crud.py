from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
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
    
    @staticmethod
    def delete(db: Session, expense_id: int) -> bool:
        """Delete an expense"""
        db_expense = ExpenseCRUD.get_by_id(db, expense_id)
        if db_expense:
            db.delete(db_expense)
            db.commit()
            return True
        return False


class AnalyticsCRUD:
    @staticmethod
    def get_date_range_start(period: str) -> Optional[datetime]:
        """Get the start date for the specified time period"""
        now = datetime.now()
        
        if period == "week":
            return now - timedelta(days=7)
        elif period == "month":
            return now - timedelta(days=30)
        elif period == "quarter":
            return now - timedelta(days=90)
        elif period == "year":
            return now - timedelta(days=365)
        else:  # all_time
            return None
    
    @staticmethod
    def get_total_spending(db: Session, user_id: int, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get total spending for a user with optional date filter"""
        # Base query for total spending
        query = db.query(func.sum(Expense.amount)).filter(Expense.owner_id == user_id)
        if start_date:
            query = query.filter(Expense.date >= start_date)
        
        total_spent = query.scalar() or 0.0
        
        # Get expense count
        count_query = db.query(func.count(Expense.id)).filter(Expense.owner_id == user_id)
        if start_date:
            count_query = count_query.filter(Expense.date >= start_date)
        
        expense_count = count_query.scalar() or 0
        avg_per_expense = total_spent / expense_count if expense_count > 0 else 0.0
        
        return {
            "total_spent": round(total_spent, 2),
            "expense_count": expense_count,
            "average_per_expense": round(avg_per_expense, 2)
        }
    
    @staticmethod
    def get_spending_by_category(db: Session, user_id: int, start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get spending breakdown by category"""
        query = db.query(
            Category.name,
            Category.id,
            func.sum(Expense.amount).label('total_spent'),
            func.count(Expense.id).label('expense_count'),
            func.avg(Expense.amount).label('average_amount')
        ).join(
            Expense, Category.id == Expense.category_id
        ).filter(
            Expense.owner_id == user_id
        ).group_by(Category.id, Category.name)
        
        if start_date:
            query = query.filter(Expense.date >= start_date)
        
        results = query.all()
        
        # Calculate total for percentage calculation
        total_spent = sum(result.total_spent for result in results)
        
        category_breakdown = []
        for result in results:
            percentage = (result.total_spent / total_spent * 100) if total_spent > 0 else 0
            category_breakdown.append({
                "category_id": result.id,
                "category_name": result.name,
                "total_spent": round(result.total_spent, 2),
                "expense_count": result.expense_count,
                "average_amount": round(result.average_amount, 2),
                "percentage_of_total": round(percentage, 2)
            })
        
        # Sort by total spent (descending)
        category_breakdown.sort(key=lambda x: x["total_spent"], reverse=True)
        
        return category_breakdown
    
    @staticmethod
    def get_daily_spending(db: Session, user_id: int, days: int) -> List[Dict[str, Any]]:
        """Get daily spending breakdown for the last N days"""
        start_date = datetime.now() - timedelta(days=days)
        
        daily_data = db.query(
            func.date(Expense.date).label('expense_date'),
            func.sum(Expense.amount).label('daily_total'),
            func.count(Expense.id).label('daily_count')
        ).filter(
            and_(
                Expense.owner_id == user_id,
                Expense.date >= start_date
            )
        ).group_by(
            func.date(Expense.date)
        ).order_by(
            func.date(Expense.date)
        ).all()
        
        daily_breakdown = []
        for row in daily_data:
            daily_breakdown.append({
                "date": row.expense_date.isoformat(),
                "total_spent": round(row.daily_total, 2),
                "expense_count": row.daily_count
            })
        
        return daily_breakdown
    
    @staticmethod
    def get_period_comparison(db: Session, user_id: int, period_days: int) -> Dict[str, Any]:
        """Compare spending between current and previous period"""
        now = datetime.now()
        
        # Current period
        current_start = now - timedelta(days=period_days)
        current_spending = db.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.owner_id == user_id,
                Expense.date >= current_start
            )
        ).scalar() or 0.0
        
        # Previous period
        previous_start = now - timedelta(days=period_days * 2)
        previous_end = now - timedelta(days=period_days)
        previous_spending = db.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.owner_id == user_id,
                Expense.date >= previous_start,
                Expense.date < previous_end
            )
        ).scalar() or 0.0
        
        # Calculate metrics
        difference = current_spending - previous_spending
        percentage_change = 0.0
        if previous_spending > 0:
            percentage_change = (difference / previous_spending) * 100
        
        return {
            "current_spending": round(current_spending, 2),
            "previous_spending": round(previous_spending, 2),
            "difference": round(difference, 2),
            "percentage_change": round(percentage_change, 2),
            "trend": "increased" if difference > 0 else "decreased" if difference < 0 else "unchanged"
        }
    
