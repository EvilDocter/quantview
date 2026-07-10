"""
QuantView — Relationship Extractor Service

Extracts strategic connections (competitor, customer, supplier, subsidiary)
between companies from raw narrative documents.
"""

import httpx
import logging
import json
from app.config import get_settings

logger = logging.getLogger("relationship_extractor")
settings = get_settings()

class RelationshipExtractor:
    """Invokes Qwen model server to parse corporate ecosystem relationships."""

    @staticmethod
    async def extract_relationships(text: str, source_company: str) -> list[dict]:
        """Runs relationship classification over financial transcript/AR text block."""
        prompt = f"""
Analyze the financial report excerpt for {source_company}. Identify any business relationships.
Look for:
1. COMPETES_WITH: Competitors.
2. SUPPLIES_TO: Customers.
3. BUYS_FROM: Suppliers.
4. SUBSIDIARY_OF: Parent company or subsidiary.

Return ONLY a valid JSON list matching this structure:
[
  {{"entity": "Entity Name", "type": "COMPETES_WITH", "notes": "compete in EV"}}
]

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
                    if "[" in raw_text:
                        start = raw_text.find("[")
                        end = raw_text.rfind("]") + 1
                        return json.loads(raw_text[start:end])
        except Exception as e:
            logger.error(f"Relationship extraction call failed: {e}")
            
        return []
