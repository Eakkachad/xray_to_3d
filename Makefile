.PHONY: setup dev frontend backend build clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ──────────────────────────────────────────────

setup: ## Full setup: conda env + backend deps + frontend deps
	@bash setup.sh

setup-backend: ## Install backend Python dependencies
	pip install -r server/requirements.txt

setup-frontend: ## Install frontend dependencies with pnpm
	cd web && pnpm install

# ── Development ────────────────────────────────────────

dev: ## Run frontend + backend concurrently
	@echo "Starting backend and frontend..."
	@make backend &
	@sleep 2
	@make frontend

frontend: ## Run frontend dev server (port 5173)
	cd web && pnpm dev

backend: ## Run backend API server (port 8000)
	cd server && python main.py

# ── Production ─────────────────────────────────────────

build: ## Build frontend for production
	cd web && pnpm build

docker-up: ## Start with Docker Compose
	docker compose up --build -d

docker-down: ## Stop Docker Compose
	docker compose down

# ── Utilities ──────────────────────────────────────────

clean: ## Remove inference output cache
	rm -rf output/web_cache/*
	@echo "Cache cleared."

check-data: ## Check if data and pretrained models exist
	@echo "Checking data files..."
	@ls data/*.pickle 2>/dev/null && echo "✓ Data files found" || echo "✗ No .pickle files in data/ — download from Google Drive"
	@echo ""
	@echo "Checking pretrained models..."
	@ls pretrained/*.tar 2>/dev/null && echo "✓ Pretrained models found" || echo "✗ No .tar files in pretrained/ — download from Google Drive"
