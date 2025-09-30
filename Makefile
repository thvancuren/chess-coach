# Chess Coach Makefile

.PHONY: help up down build dev backend frontend test clean seed

help: ## Show this help message
	@echo "Chess Coach - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services with docker-compose
	docker-compose up --build

down: ## Stop all services
	docker-compose down

build: ## Build all Docker images
	docker-compose build

dev: ## Start development environment
	docker-compose up db redis
	@echo "Starting backend..."
	cd apps/backend && python -m app.worker &
	cd apps/backend && uvicorn app.main:app --reload &
	@echo "Starting frontend..."
	cd apps/frontend && npm run dev

backend: ## Start only backend services
	docker-compose up db redis backend

frontend: ## Start only frontend
	cd apps/frontend && npm run dev

test: ## Run tests
	cd apps/backend && pytest

clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

seed: ## Seed database with demo data
	cd apps/backend && python ../scripts/seed_demo.py

migrate: ## Run database migrations
	cd apps/backend && alembic upgrade head

lichess: ## Download Lichess database slice
	python scripts/download_lichess_slice.py --year 2023 --month 1 --sample-size 1000

install: ## Install dependencies
	cd apps/backend && pip install -e .
	cd apps/frontend && npm install

setup: install migrate seed ## Complete setup for development

