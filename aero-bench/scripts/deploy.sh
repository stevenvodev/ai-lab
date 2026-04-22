#!/usr/bin/env bash

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Set Docker host for OrbStack
export DOCKER_HOST="unix://$HOME/.orbstack/run/docker.sock"

HEALTH_CHECK_RETRIES=30
HEALTH_CHECK_INTERVAL=2

log_info "=== Deploying Aero-Bench services ==="

# Ensure log file exists
LOG_FILE="system_metrics.log"
if [ ! -f "$LOG_FILE" ]; then
    log_warn "Log file $LOG_FILE does not exist, creating..."
    touch "$LOG_FILE"
fi

# Ensure Docker Compose is available
if ! command -v docker-compose &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Start services
log_step "Starting services with ${DOCKER_COMPOSE}..."
${DOCKER_COMPOSE} up -d || {
    log_error "Failed to start services"
    exit 1
}

log_info "Waiting for services to be ready..."

# Function to check Ollama health
check_ollama_health() {
    curl -s http://localhost:11434/api/tags > /dev/null 2>&1
}

# Function to check agent health
check_agent_health() {
    curl -s http://localhost:8000/health > /dev/null 2>&1
}

# Wait for Ollama
log_step "Checking Ollama health..."
for i in $(seq 1 ${HEALTH_CHECK_RETRIES}); do
    if check_ollama_health; then
        log_info "Ollama is ready"
        break
    fi
    if [ $i -eq ${HEALTH_CHECK_RETRIES} ]; then
        log_error "Ollama failed to become ready after ${HEALTH_CHECK_RETRIES} attempts"
        exit 1
    fi
    sleep ${HEALTH_CHECK_INTERVAL}
done

# Wait for agent
log_step "Checking agent health..."
for i in $(seq 1 ${HEALTH_CHECK_RETRIES}); do
    if check_agent_health; then
        log_info "Agent is ready"
        break
    fi
    if [ $i -eq ${HEALTH_CHECK_RETRIES} ]; then
        log_error "Agent failed to become ready after ${HEALTH_CHECK_RETRIES} attempts"
        ${DOCKER_COMPOSE} logs agent
        exit 1
    fi
    sleep ${HEALTH_CHECK_INTERVAL}
done

# Verify llama3:8b is available in containerized Ollama
log_step "Verifying llama3:8b model..."
sleep 5  # Give Ollama time to pull the model
for i in $(seq 1 ${HEALTH_CHECK_RETRIES}); do
    if ${DOCKER_COMPOSE} exec -T ollama ollama list 2>&1 | grep -q "llama3:8b"; then
        log_info "llama3:8b model is available"
        break
    fi
    if [ $i -eq ${HEALTH_CHECK_RETRIES} ]; then
        log_warn "llama3:8b model may not be available yet, but continuing..."
        break
    fi
    sleep ${HEALTH_CHECK_INTERVAL}
done

echo ""
log_info "=== Deployment complete ==="
log_info "Services running:"
log_info "  - Ollama: http://localhost:11434"
log_info "  - Agent API: http://localhost:8000"
log_info "  - Telemetry: container 'aero-telemetry'"
echo ""
log_info "Run 'make test' to verify the setup"
