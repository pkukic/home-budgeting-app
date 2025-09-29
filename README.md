We want you to support financial independence, therefore we want you to create a simple Home Budget application. Since you are primarily a backend developer, you will create a simple REST API. On top of that API, the client app will be added later. 

Tech stack: 
- any framework
- any RDB
- output should be JSON formatted
- API is documented (Swagger or similar)

Features:
- user authentication (register, login)
- entities and attributes are defined by you, and what you think is important
- for simplicity, every user has a predefined X amount of money on their account
- categories CRUD
- expenses CRUD (spending money = adding expenses)
- every bill has a relation to a category
- filter bills by parameters (category, price min/max, any other parameter)
- data aggregation endpoint (example: money spent in last month, quarter, year, ...)

Bonus:
- there are predefined categories of your own choice (food, car, accomodation, gifts...)
- tests

Example: 
POST category 
{ 
  "name": "food" 
} 
 
GET categories 
[ 
  { 
    "id": 1, 
    "name": "food" 
  } 
] 
 
POST expense 
{ 
  "description":  "Groceries shopping", 
  "amount": 123,45, 
  "categoryId": 1 
} 
 
GET expenses 
[ 
  { 
    "id": 1 
    "description":  "Groceries shopping", 
    "amount": 123,45, 
    "category": { 
      "id": 1, 
      "name": "food" 
    } 
  } 
]