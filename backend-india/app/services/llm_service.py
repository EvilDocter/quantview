"""
QuantView — LLM Router Service

Routes requests between Ollama and Google Gemini API with automatic dual failover.
"""

import httpx
import asyncio
import logging
import google.generativeai as genai
from app.config import get_settings

logger = logging.getLogger("llm_service")

# Valid Gemini models verified from Google API
GEMINI_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-pro-latest",
]

class LLMService:
    @staticmethod
    async def generate(
        prompt: str, temperature: float = 0.2, max_tokens: int = 2500
    ) -> str:
        """
        Generate a response with automatic multi-provider fallback.
        Tries primary provider first; if it returns empty or fails, tries secondary.
        """
        settings = get_settings()
        primary = settings.llm_provider.lower()
        
        # Ensure Gemini is initialized if key present
        if settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
            except Exception as e:
                logger.warning(f"Failed configuring Gemini API key: {e}")

        # Safety: trim prompt length to avoid prompt bloat
        if len(prompt) > 12000:
            prompt = prompt[:12000] + "\n...[truncated for context limits]..."

        # Attempt 1: Primary provider
        response_text = ""
        if primary == "ollama":
            # Give Ollama up to 25s; if slow, fallback to Gemini instantly
            try:
                response_text = await asyncio.wait_for(
                    LLMService._ollama(prompt, temperature, max_tokens),
                    timeout=25.0
                )
            except asyncio.TimeoutError:
                logger.warning("Ollama evaluation exceeded 25s timeout limit.")
                response_text = ""
            except Exception as e:
                logger.warning(f"Ollama failed: {e}")
                response_text = ""

            if not response_text and settings.gemini_api_key:
                logger.warning("Primary provider (Ollama) unavailable/timeout. Falling back to Gemini API...")
                response_text = await LLMService._gemini(prompt, temperature, max_tokens)
        else:
            response_text = await LLMService._gemini(prompt, temperature, max_tokens)
            if not response_text:
                logger.warning("Primary provider (Gemini) failed/empty. Falling back to Ollama...")
                response_text = await LLMService._ollama(prompt, temperature, max_tokens)

        return response_text

    @staticmethod
    async def _gemini(prompt: str, temperature: float, max_tokens: int) -> str:
        """Call Gemini API with verified model sequence."""
        settings = get_settings()
        if not settings.gemini_api_key:
            logger.warning("Gemini API key not configured")
            return ""

        try:
            genai.configure(api_key=settings.gemini_api_key)
        except Exception:
            pass

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
                if response and hasattr(response, "text") and response.text:
                    logger.info(f"Successfully generated response using Gemini model '{model_name}' ({len(response.text)} chars)")
                    return response.text
            except Exception as e:
                logger.warning(f"Gemini model '{model_name}' failed: {e}")
                await asyncio.sleep(0.5)
                continue

        logger.error("Gemini: exhausted all fallback models")
        return ""

    @staticmethod
    async def _ollama(prompt: str, temperature: float, max_tokens: int) -> str:
        """Call Ollama server endpoint."""
        settings = get_settings()
        try:
            logger.info(f"Attempting Ollama generation ({settings.ai_server_url}) model={settings.llm_reasoning_model}")
            async with httpx.AsyncClient(timeout=30.0) as client:
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
                    resp_json = response.json()
                    res = resp_json.get("response", "")
                    if res and len(res.strip()) > 0:
                        logger.info(f"Successfully generated response using Ollama ({len(res)} chars)")
                        return res
                else:
                    logger.warning(f"Ollama returned HTTP {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
        return ""
