.PHONY: install build deploy test stream-telemetry start stop clean help

# Default target
help:
	@echo "aero-bench - Local AI Root Cause Analysis POC"
	@echo ""
	@echo "Available targets:"
	@echo "  install          - Install dependencies and setup environment"
	@echo "  build            - Build Docker images"
	@echo "  deploy           - Deploy services and run health checks"
	@echo "  start            - Start existing containers"
	@echo "  stop             - Stop running containers"
	@echo "  test             - Run integration tests against the agent"
	@echo "  stream-telemetry - Start the telemetry simulator"
	@echo "  clean            - Remove generated files and stop containers"

install:
	@echo "=== Installing dependencies ==="
	@./scripts/install.sh

build:
	@echo "=== Building Docker images ==="
	@./scripts/build.sh

deploy:
	@echo "=== Deploying services ==="
	@./scripts/deploy.sh

start:
	@echo "=== Starting services ==="
	@docker-compose up -d
	@echo "Services started"

stop:
	@echo "=== Stopping services ==="
	@docker-compose down
	@echo "Services stopped"

test:
	@echo "=== Running tests ==="
	@./scripts/test.sh

stream-telemetry:
	@echo "=== Starting telemetry simulator ==="
	@cd src/telemetry && python simulator.py

clean:
	@echo "=== Cleaning up ==="
	@docker-compose down 2>/dev/null || true
	@rm -f system_metrics.log 2>/dev/null || true
	@rm -rf system_metrics.log 2>/dev/null || true
	@rm -rf src/telemetry/__pycache__ src/agent/__pycache__
	@echo "Clean complete"
