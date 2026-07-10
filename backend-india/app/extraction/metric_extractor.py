"""
QuantView — Financial Metric Extractor Service

Leverages Qwen 2.5 3B parser to extract and normalize raw metrics (Revenue, Capex) from unstructured text segments.
"""

import httpx
import logging
import json
from app.config import get_settings

logger = logging.getLogger("metric_extractor")
settings = get_settings()

class MetricExtractor:
    """Extracts raw financial figures from text segments using the extraction model."""

    @staticmethod
    async def extract_metrics(text: str) -> list[dict]:
        prompt = f"""
Identify and extract key financial metric disclosures from the text block.
Examples include Revenue, Net Profit, CapEx, EBITDA.

Return ONLY a valid JSON list matching this structure:
[
  {{"metric": "Revenue", "value": 5000.0, "unit": "Crores", "period": "FY24"}}
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
            logger.error(f"Metric extraction call failed: {e}")
            
        return []
