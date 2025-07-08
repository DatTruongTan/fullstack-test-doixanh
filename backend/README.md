# TodoList API Backend

A FastAPI backend for a TodoList application with authentication and task management.

## Features

- User authentication with JWT tokens
- Task CRUD operations
- Task search functionality
- Role-based permissions

## Project Structure

```
backend/
│
├── app/                     # Main application package
│   ├── api/                 # API endpoints
│   │   ├── endpoints/       # API route handlers
│   │   │   ├── auth.py      # Authentication endpoints
│   │   │   └── tasks.py     # Task endpoints
│   │   └── api.py           # API router aggregation
│   │
│   ├── core/                # Core application code
│   │   ├── config.py        # Application configuration
│   │   ├── deps.py          # Dependency injection
│   │   └── security.py      # Security utilities
│   │
│   ├── crud/                # CRUD operations
│   │   ├── user.py          # User CRUD operations
│   │   └── task.py          # Task CRUD operations
│   │
│   ├── db/                  # Database related code
│   │   ├── base.py          # Database models import for Alembic
│   │   └── session.py       # Database session setup
│   │
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py          # User model
│   │   └── task.py          # Task model
│   │
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py          # User schemas
│   │   ├── task.py          # Task schemas
│   │   └── token.py         # Authentication token schemas
│   │
│   └── main.py              # FastAPI application creation
│
├── requirements.txt         # Project dependencies
└── main.py                  # Application entry point
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the server is running, you can access:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /register` - Register a new user
- `POST /token` - Login and get access token

### Tasks
- `GET /tasks` - Get all user's tasks
- `POST /tasks` - Create a new task
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task
- `GET /tasks/search/?query=example` - Search for tasks 