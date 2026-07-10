# QuantView Indian Market Backend

Backend service for the QuantView Indian Market AI Financial Research Platform.

## Tech Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (Neon), Qdrant, Neo4j, OpenSearch, Redis
- **AI**: Qwen 2.5 7B/3B via Ollama, BGE-large-en-v1.5 embeddings
- **Agent Framework**: LangGraph
- **Task Queue**: Celery + Redis

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8001
```

## Environment Variables
Copy `.env.example` to `.env` and fill in your credentials.
