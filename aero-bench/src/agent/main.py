"""
AI Agent - FastAPI server for Root Cause Analysis
Reads system metrics logs and uses Ollama/llama3:8b for RCA
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ollama_client import OllamaClient, create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", "/app/data/system_metrics.log")
OLLAMA_CLIENT = create_client()

# FastAPI app
app = FastAPI(
    title="Aero-Bench AI Agent",
    description="Root Cause Analysis Agent using local LLM",
    version="1.0.0"
)


# Request/Response models
class AnalyzeRequest(BaseModel):
    """Request model for RCA analysis."""
    lines: int = Field(default=10, ge=1, le=1000, description="Number of log lines to analyze")
    context: Optional[str] = Field(default=None, description="Additional context for analysis")


class AnalyzeResponse(BaseModel):
    """Response model for RCA analysis."""
    status: str
    lines_analyzed: int
    analysis: str
    model: str
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    ollama_healthy: bool
    model_available: bool
    log_file_exists: bool


# File reading utilities
def read_log_lines(filepath: str, num_lines: int) -> list[dict]:
    """Read the last N lines from a log file."""
    log_path = Path(filepath)

    if not log_path.exists():
        logger.warning(f"Log file not found: {filepath}")
        return []

    try:
        with open(log_path, "r") as f:
            lines = f.readlines()

        # Get last N lines
        last_lines = lines[-num_lines:] if num_lines < len(lines) else lines

        # Parse JSON entries
        entries = []
        for line in last_lines:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse log line: {e}")

        return entries

    except IOError as e:
        logger.error(f"Failed to read log file: {e}")
        return []


def format_entries_for_llm(entries: list[dict]) -> str:
    """Format log entries for LLM consumption."""
    formatted = []
    for i, entry in enumerate(entries, 1):
        formatted.append(f"""--- Entry {i} ---
Timestamp: {entry.get('timestamp', 'N/A')}
Metric Type: {entry.get('metric_type', 'N/A')}
Host: {entry.get('host', 'N/A')}
Severity: {entry.get('severity', 'N/A')}
Value: {entry.get('value', 'N/A')}
Threshold: {entry.get('threshold', 'N/A')}
Details: {json.dumps(entry.get('details', {}), indent=2)}
""")
    return "\n".join(formatted)


# API endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    ollama_healthy = OLLAMA_CLIENT.is_healthy()
    model_available = OLLAMA_CLIENT.model_exists()
    log_exists = Path(LOG_FILE_PATH).exists()

    status = "healthy" if ollama_healthy and model_available else "degraded"

    return HealthResponse(
        status=status,
        ollama_healthy=ollama_healthy,
        model_available=model_available,
        log_file_exists=log_exists
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_logs(request: AnalyzeRequest):
    """
    Analyze system metrics logs for root cause.

    Reads the last N lines from the log file and generates an RCA analysis
    using the llama3:8b model via Ollama.
    """
    logger.info(f"Received analysis request: {request.lines} lines, context: {request.context}")

    # Read log entries
    entries = read_log_lines(LOG_FILE_PATH, request.lines)

    if not entries:
        raise HTTPException(
            status_code=400,
            detail="No log entries found to analyze. Ensure the telemetry simulator is running."
        )

    # Format entries for LLM
    formatted_entries = format_entries_for_llm(entries)

    logger.info(f"Analyzing {len(entries)} log entries...")

    # Generate RCA analysis
    analysis = OLLAMA_CLIENT.generate_rca_analysis(
        log_entries=formatted_entries,
        context=request.context
    )

    return AnalyzeResponse(
        status="success",
        lines_analyzed=len(entries),
        analysis=analysis,
        model=OLLAMA_CLIENT.model,
        timestamp="2026-04-22T00:00:00Z"  # Current timestamp would be added in production
    )


@app.get("/logs")
async def get_logs(limit: int = 10):
    """Get raw log entries for inspection."""
    entries = read_log_lines(LOG_FILE_PATH, limit)
    return {
        "count": len(entries),
        "entries": entries
    }


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("=" * 50)
    logger.info("Aero-Bench AI Agent starting...")
    logger.info(f"Ollama base URL: {OLLAMA_CLIENT.base_url}")
    logger.info(f"Model: {OLLAMA_CLIENT.model}")
    logger.info(f"Log file: {LOG_FILE_PATH}")
    logger.info("=" * 50)

    # Log initial health status
    ollama_healthy = OLLAMA_CLIENT.is_healthy()
    model_available = OLLAMA_CLIENT.model_exists()
    logger.info(f"Ollama healthy: {ollama_healthy}")
    logger.info(f"Model '{OLLAMA_CLIENT.model}' available: {model_available}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
