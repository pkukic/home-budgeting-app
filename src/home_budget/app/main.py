from fastapi import FastAPI
from home_budget.app.database import engine, Base
from home_budget.app.routers import categories, auth, expenses
from home_budget.app.init_categories import create_predefined_categories

# Create database tables
Base.metadata.create_all(bind=engine)

# Create predefined categories
create_predefined_categories()

app = FastAPI(
    title="Home Budget API",
    description="A simple REST API for managing personal budgets",
    version="0.1.0"
)

# Include routers
app.include_router(categories.router)
app.include_router(auth.router)
app.include_router(expenses.router)

@app.get("/")
def read_root():
    return {"message": "Home Budget API is running"}
