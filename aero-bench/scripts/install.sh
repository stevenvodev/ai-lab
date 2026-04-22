#!/usr/bin/env bash

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Set Docker host for OrbStack
export DOCKER_HOST="unix://$HOME/.orbstack/run/docker.sock"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed or not in PATH"
        return 1
    fi
    return 0
}

echo "=== Aero-Bench Dependency Check ==="
echo ""

# Check for required commands
MISSING_DEPS=()

check_command "docker" || MISSING_DEPS+=("docker")
check_command "make" || MISSING_DEPS+=("make")
check_command "git" || MISSING_DEPS+=("git")
check_command "curl" || MISSING_DEPS+=("curl")
check_command "python3" || MISSING_DEPS+=("python3")

if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
    echo "Missing dependencies: ${MISSING_DEPS[*]}"
    log_error "Please install the missing dependencies and try again."
    exit 1
fi

log_info "All basic dependencies found"

# Check Docker version
DOCKER_VERSION=$(docker --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
log_info "Docker version: ${DOCKER_VERSION:-unknown}"

# Check Ollama
if check_command "ollama"; then
    OLLAMA_VERSION=$(ollama --version 2>&1)
    log_info "Ollama: ${OLLAMA_VERSION}"
else
    log_warn "Ollama CLI not found (containerized Ollama will be used instead)"
fi

# Pull llama3:8b if not already present
echo ""
log_info "Checking for llama3:8b model..."
if ollama list 2>&1 | grep -q "llama3:8b"; then
    log_info "llama3:8b is already pulled"
else
    log_warn "llama3:8b not found, pulling now..."
    ollama pull llama3:8b || {
        log_error "Failed to pull llama3:8b. Ensure Ollama is running."
        exit 1
    }
    log_info "Successfully pulled llama3:8b"
fi

# Set up Python virtual environments
echo ""
log_info "Setting up Python virtual environments..."

if [[ ! -d "src/telemetry/venv" ]]; then
    log_info "Creating telemetry venv..."
    python3 -m venv src/telemetry/venv
    source src/telemetry/venv/bin/activate
    pip install --quiet -r src/telemetry/requirements.txt 2>/dev/null || true
fi

if [[ ! -d "src/agent/venv" ]]; then
    log_info "Creating agent venv..."
    python3 -m venv src/agent/venv
    source src/agent/venv/bin/activate
    pip install --quiet -r src/agent/requirements.txt 2>/dev/null || true
fi

log_info "=== Dependency check complete ==="
log_info "You can now run 'make build' to build Docker images"
