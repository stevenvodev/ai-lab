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

log_info "=== Running Aero-Bench tests ==="

# Check if agent is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    log_error "Agent is not responding. Please run 'make deploy' first."
    exit 1
fi

log_info "Agent is responding"

# Generate some test data if log file doesn't exist or is empty
if [ ! -s "system_metrics.log" ]; then
    log_warn "system_metrics.log is empty or missing, generating test data..."
    for i in {1..10}; do
        echo '{"timestamp": "'$(date -Iseconds)'","metric_type": "cpu_spike","host": "test-host","value": 95.5,"threshold": 90.0,"severity": "warning","details": {"cpu_usage": 95.5,"process": "nginx"}}' >> system_metrics.log
    done
fi

# Test 1: Health check
echo ""
log_info "Test 1: Health check endpoint"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
echo "${HEALTH_RESPONSE}" | jq .
if echo "${HEALTH_RESPONSE}" | grep -q '"status":"healthy"'; then
    log_info "Health check passed"
else
    log_warn "Health check response unexpected"
fi

# Test 2: Analyze latest log entries
echo ""
log_info "Test 2: Analyze log entries via RCA endpoint"
ANALYZE_RESPONSE=$(curl -s -X POST "http://localhost:8000/analyze" \
    -H "Content-Type: application/json" \
    -d '{"lines": 5}')

echo "${ANALYZE_RESPONSE}" | jq .

# Check if response contains RCA analysis
if echo "${ANALYZE_RESPONSE}" | grep -q "root\|cause\|analysis\|recommend"; then
    log_info "RCA analysis completed successfully"
else
    log_warn "RCA analysis response may be incomplete"
fi

echo ""
log_info "=== All tests completed ==="
log_info "You can view detailed logs with: docker-compose logs -f agent"
