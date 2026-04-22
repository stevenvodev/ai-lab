#!/usr/bin/env bash

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Set Docker host for OrbStack
export DOCKER_HOST="unix://$HOME/.orbstack/run/docker.sock"

log_info "=== Building Docker images ==="

# Build telemetry image
log_info "Building telemetry image..."
docker-compose build telemetry || {
    log_error "Failed to build telemetry image"
    exit 1
}

# Build agent image
log_info "Building agent image..."
docker-compose build agent || {
    log_error "Failed to build agent image"
    exit 1
}

log_info "=== Build complete ==="
log_info "You can now run 'make deploy' to start the services"
