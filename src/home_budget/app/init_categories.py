from home_budget.app.database import SessionLocal
from home_budget.app.crud import CategoryCRUD
from home_budget.app.schemas import CategoryCreate

def create_predefined_categories():
    """Create predefined categories if they don't exist"""
    db = SessionLocal()
    
    predefined_categories = [
        "Food",
        "Car",
        "Accommodation", 
        "Gifts",
        "Entertainment",
        "Healthcare",
        "Utilities",
        "Shopping",
        "Travel",
        "Education"
    ]
    
    try:
        for category_name in predefined_categories:
            # Check if category already exists
            if not CategoryCRUD.exists_by_name(db, category_name):
                category_create = CategoryCreate(name=category_name)
                CategoryCRUD.create(db, category_create)
        
        print(f"Predefined categories created successfully!")
    except Exception as e:
        print(f"Error creating predefined categories: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_predefined_categories()