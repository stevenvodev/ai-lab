"""
Ollama Client - Wrapper for local LLM inference via Ollama
Uses llama3:8b for RCA analysis
"""

import json
import logging
import os
from typing import Optional, Generator

import requests

logger = logging.getLogger(__name__)

# Configuration
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = "llama3:8b"

# RCA-focused system prompt
RCA_SYSTEM_PROMPT = """You are an expert Site Reliability Engineer (SRE) specializing in Root Cause Analysis (RCA).

Your task is to analyze system metrics and logs to identify the root cause of incidents.

When analyzing metrics:
1. Identify the primary symptom and its severity
2. Trace potential causal relationships between metrics
3. Consider temporal correlations (what happened first?)
4. Evaluate against known failure patterns
5. Provide actionable recommendations

Output format:
- Summary: Brief overview of the incident
- Root Cause: Most likely cause with confidence level
- Contributing Factors: Secondary issues that exacerbated the problem
- Evidence: Key metrics supporting your conclusion
- Recommendations: Actionable steps to resolve and prevent recurrence
- Severity Assessment: Impact level and urgency

Be specific, data-driven, and avoid speculation. When uncertain, acknowledge limitations."""


class OllamaClient:
    """Client for interacting with Ollama LLM service."""

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = MODEL_NAME
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_url = f"{self.base_url}/api/generate"

    def is_healthy(self) -> bool:
        """Check if Ollama service is healthy."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    def model_exists(self) -> bool:
        """Check if the required model is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                tags = response.json().get("models", [])
                return any(m.get("name", "").startswith(self.model) for m in tags)
            return False
        except requests.RequestException as e:
            logger.error(f"Failed to check model availability: {e}")
            return False

    def generate_rca_analysis(
        self,
        log_entries: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate RCA analysis using the LLM.

        Args:
            log_entries: The log entries to analyze
            context: Optional additional context

        Returns:
            The LLM's analysis response
        """
        prompt = f"""Analyze the following system metrics logs for root cause:

{log_entries}

{'Additional context: ' + context if context else ''}

Provide a structured RCA analysis following SRE best practices."""

        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": RCA_SYSTEM_PROMPT,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 2048
                }
            }

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            result = response.json()
            return result.get("response", "No analysis generated")

        except requests.exceptions.Timeout:
            logger.error("LLM request timed out")
            return "Analysis timed out. The LLM took too long to generate a response."
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM request failed: {e}")
            return f"Analysis failed: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {e}")
            return f"Unexpected error: {str(e)}"

    def stream_analysis(
        self,
        log_entries: str,
        context: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Stream LLM analysis response.

        Args:
            log_entries: The log entries to analyze
            context: Optional additional context

        Yields:
            Streamed tokens from the LLM
        """
        prompt = f"""Analyze the following system metrics logs for root cause:

{log_entries}

{'Additional context: ' + context if context else ''}

Provide a structured RCA analysis following SRE best practices."""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": RCA_SYSTEM_PROMPT,
            "stream": True,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 2048
            }
        }

        try:
            with requests.post(
                self.api_url,
                json=payload,
                stream=True,
                timeout=300
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.Timeout:
            logger.error("Streamed LLM request timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"Streamed LLM request failed: {e}")


def create_client() -> OllamaClient:
    """Factory function to create an OllamaClient instance."""
    return OllamaClient()
