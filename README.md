# Fullstack Task Management Application

A modern task management application built with a FastAPI backend and React frontend, featuring real-time search capabilities via Elasticsearch and efficient caching using Redis.

## Technologies

### Backend
- **FastAPI**: Python-based API framework with high performance
- **SQLAlchemy**: ORM for database interactions
- **PostgreSQL**: Primary database
- **Redis**: For caching frequently accessed data
- **Elasticsearch**: For powerful text search capabilities
- **JWT**: For authentication

### Frontend
- **React**: UI library
- **Axios**: For API communication
- **React Router**: For navigation
- **TypeScript**: For type safety

## Prerequisites

- Docker and Docker Compose
- Git

## Getting Started with Makefile

This project includes a comprehensive Makefile to simplify common development tasks. Here are the most useful commands:

```bash
# Show all available commands
make help

# Set up environment files and start all services
make start

# Stop all services
make stop

# Restart all services
make restart

# View logs from all services
make logs

# List running services
make ps

# Run database migrations
make db-migrate

# Run tests
make test

# Clean up containers, volumes, and images
make clean
```

The Makefile handles environment configuration, container management, and development workflows, making it the recommended way to interact with the project.

## Quick Start

### 1. Start the services

The simplest way to get started is using the Makefile:

```bash
make start
```

This command will:
- Create necessary .env files if they don't exist
- Start all Docker containers
- Set up the database, Redis, and Elasticsearch

Alternatively, if you prefer to use Docker Compose directly:

```bash
docker compose up -d
```

### 2. Access the application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Kibana: http://localhost:5601

## Project Structure

### Backend (./backend)

The backend follows a domain-driven design approach:

```
backend/
├── app/
│   ├── domain/            # Business entities and repository interfaces
│   │   ├── models/        # Database models
│   │   └── repositories/  # Repository interfaces
│   ├── application/       # Application services and schemas
│   │   ├── schemas/       # Pydantic models for API
│   │   └── services/      # Business logic services
│   ├── infrastructure/    # Implementation details
│   │   ├── db/            # Database configuration
│   │   ├── repositories/  # Repository implementations
│   │   └── services/      # External services (Redis, Elasticsearch)
│   └── presentation/      # API layer
│       └── routers/       # API endpoints
├── tests/                 # Unit and integration tests
└── main.py               # Application entry point
```

### Frontend (./frontend)

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # Page components
│   ├── api/             # API client services
│   ├── contexts/        # React context providers
│   ├── types/           # TypeScript type definitions
│   ├── assets/          # Images and other assets
│   ├── styles/          # CSS and style-related files
│   └── tests/           # Frontend tests
├── .env                 # Environment variables
└── package.json         # Dependencies and scripts
```

## Features

- **User Authentication**: JWT-based authentication system
- **Task Management**: Create, read, update, and delete tasks
- **Search**: Real-time task searching with Elasticsearch
- **Caching**: Redis-backed caching for performance optimization
- **Responsive UI**: Mobile-friendly frontend

## API Endpoints

The backend exposes the following API endpoints:

### Auth

- `POST /api/v1/auth/register`: Register a new user
- `POST /api/v1/auth/token`: Login and get access token (JWT)

### Tasks

- `GET /api/v1/tasks`: List all tasks for the current user
- `POST /api/v1/tasks`: Create a new task
- `GET /api/v1/tasks/{task_id}`: Get a specific task
- `PUT /api/v1/tasks/{task_id}`: Update a task
- `DELETE /api/v1/tasks/{task_id}`: Delete a task
- `GET /api/v1/tasks/search/?query={query}`: Search tasks by query string
- `GET /api/v1/tasks/reindex`: Reindex all tasks in Elasticsearch (admin only)

For detailed API documentation, visit the Swagger UI at http://localhost:8000/docs when the application is running.

## Development

The Makefile provides several commands to streamline the development process:

### Backend Development

```bash
# Run backend in development mode (with auto-reload)
make dev-backend

# Install backend dependencies locally
make backend-install

# Run database migrations
make db-migrate

# Create a new migration (replace "message" with a descriptive name)
make db-revision message="add user table"

# Run backend tests
make test

# Run tests with coverage report
make test-cov
```

### Frontend Development

```bash
# Run frontend in development mode
make dev-frontend

# Install frontend dependencies
make frontend-install

# Lint frontend code
make lint
```

### Database Management

```bash
# Initialize database migrations
make db-init

# Apply migrations
make db-migrate

# Rollback the last migration
make db-rollback
```

### Working with Containers

```bash
# Open a shell in the backend container
make shell

# View logs from all containers
make logs

# Restart all services
make restart
```

For local development outside Docker, you can still use the traditional commands:

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

## Testing

Run backend tests with:

```bash
cd backend
pytest
```

## Deployment Considerations

- Configure environment variables for production settings
- Set up proper security for the Elasticsearch and PostgreSQL instances
- Consider using managed services for databases in production

## Troubleshooting

### Docker Compose Issues

1. **PostgreSQL container fails to start**
   - Check that environment variables in docker-compose.yml match those in backend/.env
   - Consider using direct values instead of variable interpolation: `POSTGRES_USER=postgres` rather than `POSTGRES_USER=${POSTGRES_USER}`
   - Ensure the postgres volume is not corrupted with `docker volume rm fullstack-test-doixanh_postgres_data`
   - Try using the Makefile to start services: `make start` (recreates .env files if needed)

2. **Elasticsearch memory issues**
   - If Elasticsearch fails due to memory constraints, adjust the `ES_JAVA_OPTS` settings in the docker-compose.yml file

3. **Connection refused errors**
   - Make sure the services are healthy with `docker compose ps` or `make ps`
   - Check service logs with `docker compose logs <service-name>` or `make logs`
   - Verify that network connections between containers are working properly

### Backend Issues

1. **Database migration errors**
   - Run migrations manually using the Makefile: `make db-migrate`
   - If needed, rollback migrations with: `make db-rollback`

2. **Redis or Elasticsearch connection issues**
   - Check if services are running: `make ps`
   - Verify connection settings in backend/.env file
   - Test connections using the /health endpoint

### Environment Setup Issues

If you encounter environment-related issues:

1. **Missing .env files**
   - Run `make setup-env` to create default .env files

2. **Clean project state**
   - Use `make clean` to remove all containers, volumes, and cached files
   - Then restart with `make start`

## License

[MIT](LICENSE)
