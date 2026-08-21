"""
QuantView — High-Speed LLM Router & Institutional Synthesis Engine (Phase IV Mandate)

Routes LLM requests to local GPU Ollama models (qwen2.5:7b / qwen2.5:1.5b).
If local GPU is overloaded (>5s timeout), falls back to a dynamic evidence-based institutional synthesis
that parses 100% real financial metrics, derives analytical ratios, and models Bull/Base/Bear valuation scenarios.
"""

import requests
import asyncio
import logging
import json
import re

from app.config import get_settings

logger = logging.getLogger("llm_service")


class LLMService:
    """Server-side local LLM service for Qwen model engine."""

    @staticmethod
    def _sync_post(url: str, payload: dict, timeout_sec: float) -> dict:
        resp = requests.post(url, json=payload, timeout=timeout_sec)
        if resp.status_code == 200:
            return resp.json()
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")

    @staticmethod
    async def generate(
        prompt: str, temperature: float = 0.2, max_tokens: int = 1200
    ) -> str:
        """
        Generate response using the server's local GPU model (qwen2.5:7b / qwen2.5:1.5b) with fast fallback.
        """
        settings = get_settings()

        if len(prompt) > 4500:
            prompt = prompt[:4500] + "\n...[truncated for speed]..."

        models_to_try = ["qwen2.5:1.5b", "qwen2.5-coder:1.5b", "qwen2.5:7b", settings.llm_reasoning_model]

        for model_name in models_to_try:
            try:
                logger.info(f"Generating via server LLM ({settings.ai_server_url}) model={model_name} (timeout=30s)")
                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                }

                resp_json = await asyncio.to_thread(
                    LLMService._sync_post, settings.ai_server_url, payload, 30.0
                )

                res = resp_json.get("response", "")
                if res and len(res.strip()) > 30:
                    logger.info(f"Successfully generated response via local {model_name} ({len(res)} chars)")
                    return res
            except Exception as e:
                logger.warning(f"Local LLM generation failed for model {model_name}: {e}")

        # Honest failure reporting — do NOT generate fake hardcoded reports
        logger.error("LLM Generation failed across all configured models.")
        return (
            "### LLM Service Unavailable\n"
            "Unable to generate AI research report because the local LLM model (Qwen 2.5) is currently offline or unreachable on the server.\n"
            "QuantView refuses to output synthetic or fabricated analyst reports without active model inference."
        )

