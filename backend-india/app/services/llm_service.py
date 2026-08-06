"""
QuantView — LLM Router Service

Routes requests between local Ollama and Google Gemini API.
Includes model fallback chain and rate limit retry logic.
"""

import httpx
import asyncio
import logging
import google.generativeai as genai
from app.config import get_settings

logger = logging.getLogger("llm_service")
settings = get_settings()

if settings.llm_provider == "gemini" and settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)
    logger.info("LLM provider: Gemini API configured")

# Model fallback sequence
GEMINI_MODELS = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash"]

class LLMService:
    @staticmethod
    async def generate(
        prompt: str, temperature: float = 0.2, max_tokens: int = 4000
    ) -> str:
        """Generate a response using the configured LLM provider."""
        if settings.llm_provider == "gemini":
            return await LLMService._gemini(prompt, temperature, max_tokens)
        else:
            return await LLMService._ollama(prompt, temperature, max_tokens)

    @staticmethod
    async def _gemini(prompt: str, temperature: float, max_tokens: int) -> str:
        """Call Gemini API with model fallback and retries."""
        for model_name in GEMINI_MODELS:
            try:
                logger.info(f"Attempting Gemini generation with model: {model_name}")
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    },
                )
                response = await model.generate_content_async(prompt)
                if response and response.text:
                    logger.info(f"Successfully generated response using {model_name} ({len(response.text)} chars)")
                    return response.text
            except Exception as e:
                logger.warning(f"Gemini model {model_name} failed: {e}")
                await asyncio.sleep(2)
                continue

        logger.error("Gemini: exhausted all fallback models")
        return ""

    @staticmethod
    async def _ollama(prompt: str, temperature: float, max_tokens: int) -> str:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    settings.ai_server_url,
                    json={
                        "model": settings.llm_reasoning_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        },
                    },
                )
                if response.status_code == 200:
                    return response.json().get("response", "")
        except Exception as e:
            logger.error(f"Ollama failed: {e}")
        return ""
