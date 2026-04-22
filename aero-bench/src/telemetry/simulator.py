#!/usr/bin/env python3
"""
Telemetry Simulator - Generates realistic streaming system metrics/logs
Simulates CPU spikes, disk latency anomalies, and JVM GC pauses
"""

import json
import logging
import random
import sys
import time
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
LOG_FILE = "/app/data/system_metrics.log"
INTERVAL_SECONDS = 5
HOSTNAMES = ["web-server-01", "web-server-02", "db-master-01", "cache-node-01", "app-server-03"]
PROCESS_NAMES = ["nginx", "postgres", "java", "redis-server", "node", "python", "gunicorn"]

# Metric type configurations
METRIC_TYPES = {
    "cpu_spike": {
        "base_usage": 40,
        "spike_range": (85, 100),
        "threshold": 90,
        "severity_weights": {"info": 0.3, "warning": 0.5, "critical": 0.2}
    },
    "disk_latency": {
        "base_latency_ms": 10,
        "anomaly_range": (500, 5000),
        "threshold_ms": 500,
        "severity_weights": {"info": 0.4, "warning": 0.4, "critical": 0.2}
    },
    "jvm_gc_pause": {
        "base_pause_ms": 50,
        "anomaly_range": (2000, 10000),
        "threshold_ms": 2000,
        "severity_weights": {"info": 0.3, "warning": 0.5, "critical": 0.2}
    },
    "memory_usage": {
        "base_usage": 60,
        "anomaly_range": (85, 98),
        "threshold": 85,
        "severity_weights": {"info": 0.4, "warning": 0.4, "critical": 0.2}
    },
    "connection_pool": {
        "base_usage": 30,
        "anomaly_range": (80, 100),
        "threshold": 80,
        "severity_weights": {"info": 0.3, "warning": 0.5, "critical": 0.2}
    }
}


def generate_cpu_spike(timestamp: str) -> dict:
    """Generate a CPU spike metric."""
    config = METRIC_TYPES["cpu_spike"]
    severity = random.choices(
        list(config["severity_weights"].keys()),
        weights=list(config["severity_weights"].values())
    )[0]

    if severity == "info":
        usage = random.uniform(config["base_usage"], config["threshold"] - 5)
    elif severity == "warning":
        usage = random.uniform(config["threshold"], config["spike_range"][0])
    else:  # critical
        usage = random.uniform(config["spike_range"][0], config["spike_range"][1])

    return {
        "timestamp": timestamp,
        "metric_type": "cpu_spike",
        "host": random.choice(HOSTNAMES),
        "value": round(usage, 2),
        "threshold": config["threshold"],
        "severity": severity,
        "details": {
            "cpu_usage": round(usage, 2),
            "process": random.choice(PROCESS_NAMES),
            "core_count": random.randint(4, 32),
            "load_average": round(usage / 10, 2)
        }
    }


def generate_disk_latency(timestamp: str) -> dict:
    """Generate a disk latency anomaly metric."""
    config = METRIC_TYPES["disk_latency"]
    severity = random.choices(
        list(config["severity_weights"].keys()),
        weights=list(config["severity_weights"].values())
    )[0]

    if severity == "info":
        latency = random.uniform(config["base_latency_ms"], config["threshold_ms"] - 100)
    elif severity == "warning":
        latency = random.uniform(config["threshold_ms"], config["anomaly_range"][0])
    else:  # critical
        latency = random.uniform(config["anomaly_range"][0], config["anomaly_range"][1])

    return {
        "timestamp": timestamp,
        "metric_type": "disk_latency",
        "host": random.choice(HOSTNAMES),
        "value": round(latency, 2),
        "threshold": config["threshold_ms"],
        "severity": severity,
        "details": {
            "io_wait_ms": round(latency, 2),
            "device": random.choice(["sda", "sdb", "nvme0n1", "nvme1n1"]),
            "filesystem": random.choice(["ext4", "xfs", "apfs"]),
            "read_ops": random.randint(100, 10000),
            "write_ops": random.randint(50, 5000)
        }
    }


def generate_jvm_gc_pause(timestamp: str) -> dict:
    """Generate a JVM GC pause metric."""
    config = METRIC_TYPES["jvm_gc_pause"]
    severity = random.choices(
        list(config["severity_weights"].keys()),
        weights=list(config["severity_weights"].values())
    )[0]

    if severity == "info":
        pause_ms = random.uniform(config["base_pause_ms"], config["threshold_ms"] - 500)
    elif severity == "warning":
        pause_ms = random.uniform(config["threshold_ms"], config["anomaly_range"][0])
    else:  # critical
        pause_ms = random.uniform(config["anomaly_range"][0], config["anomaly_range"][1])

    gc_types = ["G1 Young Generation", "G1 Old Generation", "Parallel Old", "CMS"]
    return {
        "timestamp": timestamp,
        "metric_type": "jvm_gc_pause",
        "host": random.choice(HOSTNAMES),
        "value": round(pause_ms, 2),
        "threshold": config["threshold_ms"],
        "severity": severity,
        "details": {
            "gc_pause_ms": round(pause_ms, 2),
            "gc_type": random.choice(gc_types),
            "heap_used_before_mb": random.randint(2000, 8000),
            "heap_used_after_mb": random.randint(1000, 7000),
            "jvm_version": random.choice(["11.0.21", "17.0.9", "21.0.1"])
        }
    }


def generate_memory_usage(timestamp: str) -> dict:
    """Generate a memory usage metric."""
    config = METRIC_TYPES["memory_usage"]
    severity = random.choices(
        list(config["severity_weights"].keys()),
        weights=list(config["severity_weights"].values())
    )[0]

    if severity == "info":
        usage = random.uniform(config["base_usage"], config["threshold"] - 5)
    elif severity == "warning":
        usage = random.uniform(config["threshold"], config["anomaly_range"][0])
    else:  # critical
        usage = random.uniform(config["anomaly_range"][0], config["anomaly_range"][1])

    return {
        "timestamp": timestamp,
        "metric_type": "memory_usage",
        "host": random.choice(HOSTNAMES),
        "value": round(usage, 2),
        "threshold": config["threshold"],
        "severity": severity,
        "details": {
            "memory_used_mb": random.randint(8000, 24000),
            "memory_total_mb": 32768,
            "swap_used_mb": random.randint(0, 2000),
            "cache_mb": random.randint(1000, 8000)
        }
    }


def generate_connection_pool(timestamp: str) -> dict:
    """Generate a connection pool metric."""
    config = METRIC_TYPES["connection_pool"]
    severity = random.choices(
        list(config["severity_weights"].keys()),
        weights=list(config["severity_weights"].values())
    )[0]

    if severity == "info":
        usage = random.uniform(config["base_usage"], config["threshold"] - 5)
    elif severity == "warning":
        usage = random.uniform(config["threshold"], config["anomaly_range"][0])
    else:  # critical
        usage = random.uniform(config["anomaly_range"][0], config["anomaly_range"][1])

    return {
        "timestamp": timestamp,
        "metric_type": "connection_pool",
        "host": random.choice(HOSTNAMES),
        "value": round(usage, 2),
        "threshold": config["threshold"],
        "severity": severity,
        "details": {
            "pool_size": random.randint(50, 200),
            "active_connections": int(usage / 100 * random.randint(50, 200)),
            "max_connections": 200,
            "wait_time_ms": random.randint(0, 500) if usage > 80 else random.randint(0, 50),
            "database": random.choice(["postgres", "mysql", "redis"])
        }
    }


def generate_metric(timestamp: str) -> dict:
    """Generate a random metric."""
    generators = [
        generate_cpu_spike,
        generate_disk_latency,
        generate_jvm_gc_pause,
        generate_memory_usage,
        generate_connection_pool
    ]
    generator = random.choice(generators)
    return generator(timestamp)


def main():
    """Main loop for telemetry generation."""
    logger.info(f"Starting telemetry simulator, writing to {LOG_FILE}")
    logger.info(f"Generating metrics every {INTERVAL_SECONDS} seconds")

    iteration = 0
    while True:
        timestamp = datetime.now(timezone.utc).isoformat()
        metric = generate_metric(timestamp)
        metric["id"] = f"metric-{iteration:06d}"

        # Write to log file
        try:
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(metric) + "\n")
            logger.info(f"Generated {metric['metric_type']} on {metric['host']} - severity: {metric['severity']}")
        except IOError as e:
            logger.error(f"Failed to write to log file: {e}")

        iteration += 1
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTelemetry simulator stopped.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
