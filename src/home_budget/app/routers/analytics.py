from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, List
from enum import Enum

from home_budget.app.database import get_db
from home_budget.app.dependencies import get_current_user_dependency
from home_budget.app.models import User
from home_budget.app.crud import AnalyticsCRUD

router = APIRouter(prefix="/analytics", tags=["analytics"])


class TimePeriod(str, Enum):
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"


@router.get("/spending/total")
def get_total_spending(
    period: TimePeriod = Query(TimePeriod.ALL_TIME, description="Time period for analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get total spending for a specific time period"""
    start_date = AnalyticsCRUD.get_date_range_start(period.value)
    spending_data = AnalyticsCRUD.get_total_spending(db, current_user.id, start_date)
    
    return {
        "period": period.value,
        **spending_data,
        "remaining_balance": round(current_user.balance, 2)
    }


@router.get("/spending/by-category")
def get_spending_by_category(
    period: TimePeriod = Query(TimePeriod.ALL_TIME, description="Time period for analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get spending breakdown by category for a specific time period"""
    start_date = AnalyticsCRUD.get_date_range_start(period.value)
    categories = AnalyticsCRUD.get_spending_by_category(db, current_user.id, start_date)
    
    total_spent = sum(cat["total_spent"] for cat in categories)
    
    return {
        "period": period.value,
        "total_spent": round(total_spent, 2),
        "categories": categories
    }


@router.get("/spending/daily")
def get_daily_spending(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get daily spending breakdown for the last N days"""
    daily_breakdown = AnalyticsCRUD.get_daily_spending(db, current_user.id, days)
    
    # Calculate summary statistics
    total_spent = sum(day["total_spent"] for day in daily_breakdown)
    total_expenses = sum(day["expense_count"] for day in daily_breakdown)
    avg_daily_spending = total_spent / days if days > 0 else 0
    
    return {
        "period_days": days,
        "total_spent": round(total_spent, 2),
        "total_expenses": total_expenses,
        "average_daily_spending": round(avg_daily_spending, 2),
        "daily_breakdown": daily_breakdown
    }


@router.get("/spending/comparison")
def get_period_comparison(
    current_period: TimePeriod = Query(TimePeriod.MONTH, description="Current period to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Compare spending between current and previous period"""
    
    # Map periods to days
    period_days_map = {
        TimePeriod.WEEK: 7,
        TimePeriod.MONTH: 30,
        TimePeriod.QUARTER: 90,
        TimePeriod.YEAR: 365
    }
    
    if current_period == TimePeriod.ALL_TIME:
        # For all_time, just return current total with no comparison
        spending_data = AnalyticsCRUD.get_total_spending(db, current_user.id)
        return {
            "current_period": current_period.value,
            "current_spending": spending_data["total_spent"],
            "previous_spending": 0.0,
            "difference": spending_data["total_spent"],
            "percentage_change": 0.0,
            "trend": "no_comparison"
        }
    
    period_days = period_days_map.get(current_period, 30)
    comparison_data = AnalyticsCRUD.get_period_comparison(db, current_user.id, period_days)
    
    return {
        "current_period": current_period.value,
        **comparison_data
    }