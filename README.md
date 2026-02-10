# Financial Tracker

A full-stack financial tracker application built with FastAPI (backend) and Vite + React (frontend).

## Project Structure

```
agentic_fin_tracker/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── transactions.py
│   │   │   ├── categories.py
│   │   │   └── dashboard.py
│   │   ├── models/           # Database models and schemas
│   │   │   ├── transaction.py
│   │   │   ├── category.py
│   │   │   └── schemas.py
│   │   ├── services/         # Business logic
│   │   │   ├── transaction_service.py
│   │   │   ├── category_service.py
│   │   │   └── dashboard_service.py
│   │   └── core/             # Core configuration
│   │       ├── config.py
│   │       └── database.py
│   ├── tests/
│   ├── main.py               # FastAPI application entry point
│   ├── requirements.txt      # Python dependencies
│   ├── .env                  # Environment variables
│   └── .env.example          # Example environment variables
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Navigation.jsx
│   │   │   ├── TransactionForm.jsx
│   │   │   ├── TransactionList.jsx
│   │   │   ├── CategoryForm.jsx
│   │   │   └── CategoryList.jsx
│   │   ├── pages/            # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Transactions.jsx
│   │   │   └── Categories.jsx
│   │   ├── services/         # API services
│   │   │   └── api.js
│   │   ├── hooks/            # Custom React hooks
│   │   ├── utils/            # Utility functions
│   │   ├── assets/           # Static assets
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── public/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── .env                  # Frontend environment variables
│   └── .env.example
├── venv/                     # Python virtual environment
├── .gitignore
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies (make sure venv is activated):
   ```bash
   # On Windows
   ..\venv\Scripts\activate

   # On Linux/Mac
   source ../venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the `DATABASE_URL` with your PostgreSQL credentials
   - Update the `SECRET_KEY` with a secure key

4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

   The API will be available at `http://localhost:8001`
   API documentation at `http://localhost:8001/docs`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update `VITE_API_BASE_URL` if needed

4. Run the development server:
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5174`

## Features

### Backend
- RESTful API with FastAPI
- PostgreSQL database integration
- SQLAlchemy ORM
- Pydantic for data validation
- CORS middleware for frontend communication
- Environment-based configuration

### Frontend
- React 18 with Vite
- React Router for navigation
- Component-based architecture
- Responsive design
- API integration with fetch

## API Endpoints

### Transactions
- `GET /api/transactions` - Get all transactions
- `POST /api/transactions` - Create a transaction
- `GET /api/transactions/{id}` - Get a specific transaction
- `PUT /api/transactions/{id}` - Update a transaction
- `DELETE /api/transactions/{id}` - Delete a transaction

### Categories
- `GET /api/categories` - Get all categories
- `POST /api/categories` - Create a category
- `GET /api/categories/{id}` - Get a specific category
- `DELETE /api/categories/{id}` - Delete a category

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

## Technologies Used

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL (psycopg2-binary)
- Uvicorn

### Frontend
- React
- Vite
- React Router
- CSS3

## Next Steps

1. Update the PostgreSQL connection in `backend/.env`
2. Create the database tables (will be done after reviewing existing PostgreSQL schema)
3. Start development with your existing PostgreSQL records
