# Makefile for fullstack-test-doixanh project

.PHONY: help start stop restart logs ps clean build dev-backend dev-frontend lint test setup-env unit-test test-cov

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup-env: ## Create .env files if they don't exist
	@if [ ! -f backend/.env ]; then \
		echo "Creating backend/.env"; \
		cp -n .env.example backend/.env 2>/dev/null || echo "# PostgreSQL\nPOSTGRES_USER=postgres\nPOSTGRES_PASSWORD=postgres\nPOSTGRES_DB=tododb\n\n# Backend\nSQLALCHEMY_DATABASE_URI=postgresql://postgres:postgres@postgres/tododb\nREDIS_URL=redis://redis:6379/0\nELASTICSEARCH_URL=http://elasticsearch:9200\n\n# JWT\nSECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7\nACCESS_TOKEN_EXPIRE_MINUTES=43200" > backend/.env; \
	fi
	@if [ ! -f frontend/.env ]; then \
		echo "Creating frontend/.env"; \
		cp -n .env.example frontend/.env 2>/dev/null || echo "# Frontend API URL\nVITE_API_URL=http://localhost:8000" > frontend/.env; \
	fi

start: setup-env ## Start all services using docker-compose
	docker-compose up -d

stop: ## Stop all services
	docker-compose down

restart: stop start ## Restart all services

logs: ## Show logs from all services
	docker-compose logs -f

ps: ## List running services
	docker-compose ps

clean: ## Remove all containers, volumes, and images
	docker-compose down -v --rmi all

build: setup-env ## Build or rebuild services
	docker-compose build

dev-backend: setup-env ## Run backend in development mode
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: setup-env ## Run frontend in development mode
	cd frontend && npm run dev

lint: ## Run linters
	cd frontend && npm run lint
	cd backend && python -m flake8

test: ## Run all tests
	cd backend && python -m pytest

db-init: ## Initialize alembic for migrations
	cd backend && alembic init -t generic app/infrastructure/db/migrations

db-migrate: ## Run database migrations
	cd backend && alembic upgrade head

db-revision: ## Create a new migration revision
	cd backend && alembic revision --autogenerate -m "$(message)"

db-rollback: ## Rollback last database migration
	cd backend && alembic downgrade -1

shell: ## Open a shell in the backend container
	docker-compose exec api /bin/sh

frontend-install: ## Install frontend dependencies
	cd frontend && npm install

backend-install: ## Install backend dependencies
	cd backend && pip install -r requirements.txt 

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type d -name "dist" -exec rm -r {} +
	find . -type d -name "build" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +