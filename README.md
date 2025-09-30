# Home Budget API

A simple REST API for personal expense tracking and budget management built with FastAPI. Track your spending, manage categories, and get detailed analytics on your financial habits.

## Features

- **User authentication** - Secure JWT-based registration and login
- **Expense tracking** - Add, edit, and delete expenses with automatic balance deduction
- **Category management** - Organize expenses with predefined and custom categories
- **Advanced filtering** - Filter expenses by category, amount range, and date
- **Analytics & reporting** - Get spending insights by time periods and categories
- **Balance management** - Track remaining balance (**starts with $1000.00**)

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for Python package management.

### Prerequisites
- uv package manager

### Install uv (if not already installed)
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup project
```bash
# Clone the repository
git clone <repository-url>
cd home-budget

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate     # On Windows
```

## Usage

### Setup the key environment variable
```bash
# On Linux/macOS
export JWT_SECRET_KEY='your_secret_key_here'

# On Windows (PowerShell)
$env:JWT_SECRET_KEY='your_secret_key_here'
```     

### Start the server
```bash
# Run the FastAPI server
python main.py

# Server will start at http://0.0.0.0:8000
```

### API documentation
Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://0.0.0.0:8000/docs
- **ReDoc**: http://0.0.0.0:8000/redoc
- **OpenAPI JSON**: http://0.0.0.0:8000/openapi.json

### Common endpoints

#### Authentication
```bash
# Register a new user
POST /auth/register
{
  "email": "user@example.com",
  "password": "securepassword",
}

# Login
POST /auth/login
Content-Type: application/x-www-form-urlencoded
username=user@example.com&password=securepassword

# Get current user info
GET /auth/me
Authorization: Bearer <your-jwt-token>
```

#### Categories
```bash
# Get all categories
GET /categories/

# Create a category
POST /categories/
{
  "name": "Groceries"
}
```

#### Expenses
```bash
# Create an expense (deducts from balance)
POST /expenses/
{
  "amount": 50.00,
  "description": "Weekly groceries",
  "category_id": 1
}

# Get all expenses with filtering
GET /expenses/?category_id=1&min_amount=10.00&max_amount=100.00

# Get single expense
GET /expenses/{expense_id}
```

#### Analytics
```bash
# Total spending by period
GET /analytics/spending/total?period=month

# Spending by category
GET /analytics/spending/by-category?period=week

# Daily spending breakdown
GET /analytics/spending/daily?days=30

# Compare periods
GET /analytics/spending/comparison?current_period=month
```

## Testing

Test files are available in the `tests/` directory:

- `tests/login.http` - Login endpoints
- `tests/expenses.http` - Managing endpoints
- `tests/auth.http` - Authentication endpoints
- `tests/categories.http` - Category management
- `tests/expenses.http` - Expense tracking

Use VS Code with the REST Client extension or any HTTP client to run these tests.

## Configuration

The application uses the following default settings:
- **Database**: SQLite (`home_budget.db`)
- **Starting Balance**: $1000.00 per user
- **JWT Secret**: Auto-generated (set `JWT_SECRET_KEY` env var for production)
- **Token Expiry**: 30 minutes

## Security

- Passwords are hashed using bcrypt
- JWT tokens for stateless authentication
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy ORM

## Predefined categories

The system comes with these default expense categories:
- Food
- Car
- Accomodation
- Gifts
- Entertainment
- Healthcare
- Utilities
- Shopping
- Travel
- Education

## License

This project is licensed under the MIT License.
