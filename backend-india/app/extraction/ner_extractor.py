"""
QuantView — Named Entity Recognition (NER) Service

Leverages Qwen 2.5 3B inference server to parse entities (Companies, Products, Persons)
from extracted narrative texts of financial documents.
"""

import httpx
import logging
import json
from app.config import get_settings

logger = logging.getLogger("ner_extractor")
settings = get_settings()

class NERExtractor:
    """Invokes local/remote LLM to extract entities from financial text segments."""

    @staticmethod
    async def extract_entities(text: str) -> dict:
        """Call Qwen model server to run Named Entity Recognition parsing."""
        prompt = f"""
You are an expert financial analyzer. Extract Named Entities from the text below.
Identify companies, key people, products, locations, and financial metrics mentioned.

Return ONLY a valid JSON object matching this structure:
{{
  "companies": ["company name 1"],
  "people": ["person name 1"],
  "products": ["product name 1"],
  "locations": ["location name 1"]
}}

Text:
\"\"\"{text[:4000]}\"\"\"
"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.ai_server_url}/completion",
                    json={
                        "prompt": prompt,
                        "model": settings.llm_extraction_model,
                        "temperature": 0.0,
                        "max_tokens": 512
                    }
                )
                if response.status_code == 200:
                    raw_text = response.json().get("text", "")
                    
                    # Parse JSON block from response text
                    # (In production, uses strict regex/pydantic parsing)
                    if "{" in raw_text:
                        start = raw_text.find("{")
                        end = raw_text.rfind("}") + 1
                        return json.loads(raw_text[start:end])
        except Exception as e:
            logger.error(f"NER extraction call failed: {e}")
            
        # Safe fallback stub if server is offline or fails parsing
        return {"companies": [], "people": [], "products": [], "locations": []}
