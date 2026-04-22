# Aero-Bench - AI Root Cause Analysis

A 100% local, end-to-end AI Proof of Concept focusing on automated Root Cause Analysis (RCA) of live system metrics and logs.

## Overview

This POC demonstrates how a LLM (llama3:8b via Ollama) can analyze streaming system metrics and logs to provide automated RCA insights. The entire stack runs locally with no cloud dependencies.

**AI-Driven RCA Sample Output:**
```
Summary: The system experienced a series of incidents characterized by increased garbage collection pauses, connection pool warnings, memory usage warnings, and disk latency issues.
Root Cause: The most likely cause of the incident with a confidence level of 90% is insufficient heap size, leading to increased garbage collection pauses.
Recommendations:
1. Increase JVM heap size: Adjust the JVM heap size to accommodate the growing memory demands.
2. Monitor memory usage: Closely monitor memory usage to identify potential issues.
3. Optimize connection pool settings**: Review and optimize connection pool settings.
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Telemetry   │────▶│ system_      │────▶│ Agent       │
│ Simulator   │     │ metrics.log  │     │ (FastAPI)   │
│             │     │              │     │             │
│ Generates   │     │              │     │ RCA         │
│ JSON logs   │     │              │     │ Analysis    │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                                                ▼
                                      ┌─────────────────┐
                                      │ Ollama          │
                                      │ (llama3:8b)     │
                                      │                 │
                                      │ LLM Inference   │
                                      └─────────────────┘
```

## Prerequisites

- **Docker** & Docker Compose
- **Make** (for build automation)
- **Git**
- **Python 3.11+** (for local development)
- **Ollama** (optional, for local model management)
- **macOS** with Apple Silicon (M-series chips recommended)

## Quick Start

### 1. Install Dependencies

```bash
make install
```

This will:
- Check for required dependencies (Docker, Make, Git, Python)
- Pull `llama3:8b` model if not already present
- Set up Python virtual environments

### 2. Build Docker Images

```bash
make build
```

### 3. Deploy Services

```bash
make deploy
```

This starts:
- **Ollama** (port 11434) - LLM inference service
- **Telemetry** (container) - Log generator
- **Agent** (port 8000) - RCA analysis API

### 4. Run Tests

```bash
make test
```

Verifies the setup by:
- Checking health endpoints
- Sending sample log entries for analysis
- Validating RCA output

### 5. Stream Telemetry (Optional)

```bash
make stream-telemetry
```

Runs the telemetry simulator locally to generate mock metrics.

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

**Example Response:**
```json
{
  "status": "healthy",
  "ollama_healthy": true,
  "model_available": true,
  "log_file_exists": true
}
```

### RCA Analysis
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"lines": 10}'
```

**Example Response:**
```json
{
  "status": "success",
  "lines_analyzed": 5,
  "analysis": "**Summary:**\n\nThe system experienced a series of incidents characterized by increased garbage collection pauses, connection pool warnings, memory usage warnings, and disk latency issues.\n\n**Root Cause:**\n\nThe most likely cause of the incident with a confidence level of 90% is **insufficient heap size**, leading to increased garbage collection pauses.\n\n**Recommendations:**\n\n1. **Increase JVM heap size**: Adjust the JVM heap size to accommodate the growing memory demands.\n2. **Monitor memory usage**: Closely monitor memory usage to identify potential issues.\n3. **Optimize connection pool settings**: Review and optimize connection pool settings.",
  "model": "llama3:8b",
  "timestamp": "2026-04-22T00:00:00Z"
}
```

### Get Raw Logs
```bash
curl "http://localhost:8000/logs?limit=20"
```

## Log Format

The telemetry simulator generates JSON-formatted logs:

```json
{
  "timestamp": "2026-04-22T12:00:00+00:00",
  "metric_type": "cpu_spike",
  "host": "web-server-01",
  "value": 95.5,
  "threshold": 90.0,
  "severity": "warning",
  "details": {
    "cpu_usage": 95.5,
    "process": "nginx",
    "core_count": 16,
    "load_average": 9.55
  }
}
```

Supported metric types:
- `cpu_spike` - CPU utilization anomalies
- `disk_latency` - Disk I/O latency issues
- `jvm_gc_pause` - JVM garbage collection pauses
- `memory_usage` - Memory consumption levels
- `connection_pool` - Database connection pool exhaustion

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `LOG_FILE_PATH` | `/app/system_metrics.log` | Path to log file |

### Making Changes

1. **Telemetry Simulator**: Edit `src/telemetry/simulator.py`
2. **Agent Logic**: Edit `src/agent/main.py` and `src/agent/ollama_client.py`
3. **Docker Images**: Edit respective `Dockerfile`s

## Troubleshooting

### Ollama not responding
```bash
docker-compose logs ollama
```

### Agent failing to analyze
```bash
docker-compose logs agent
```

### Check if model is loaded
```bash
docker-compose exec ollama ollama list
```

### Restart services
```bash
docker-compose restart
```

## Project Structure

```
.
├── .gitignore
├── Makefile
├── docker-compose.yml
├── README.md
├── scripts/
│   ├── install.sh
│   ├── build.sh
│   ├── deploy.sh
│   └── test.sh
├── src/
│   ├── telemetry/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── simulator.py
│   └── agent/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── main.py
│       └── ollama_client.py
└── system_metrics.log (generated)
```

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- [Ollama](https://ollama.com) - Local LLM serving
- [llama3:8b](https://ollama.com/library/llama3) - Meta's open-weight model
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [LangChain](https://langchain.com) - LLM orchestration framework
