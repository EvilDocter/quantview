"""
QuantView — OpenSearch Connection

Client for Bonsai free tier — handles index creation,
document indexing, and full-text keyword search.
"""

from opensearchpy import OpenSearch
from typing import Optional
from app.config import get_settings

settings = get_settings()

# ── OpenSearch Client ────────────────────────────────────────────
_opensearch_client: Optional[OpenSearch] = None


def get_opensearch_client() -> OpenSearch:
    """Get or create the OpenSearch client."""
    global _opensearch_client
    if _opensearch_client is None:
        auth = None
        if settings.opensearch_user and settings.opensearch_password:
            auth = (settings.opensearch_user, settings.opensearch_password)

        _opensearch_client = OpenSearch(
            hosts=[settings.opensearch_url],
            http_auth=auth,
            use_ssl=settings.opensearch_url.startswith("https"),
            verify_certs=True,
            ssl_show_warn=False,
            timeout=30,
        )
    return _opensearch_client


def init_opensearch_index():
    """Create the document search index if it doesn't exist."""
    client = get_opensearch_client()
    index_name = settings.opensearch_index

    if not client.indices.exists(index=index_name):
        mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,  # Free tier: single node
                "analysis": {
                    "analyzer": {
                        "financial_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop", "snowball"],
                        }
                    }
                },
            },
            "mappings": {
                "properties": {
                    "company_id": {"type": "integer"},
                    "company_symbol": {"type": "keyword"},
                    "company_name": {"type": "text"},
                    "document_type": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "financial_analyzer",
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "financial_analyzer",
                    },
                    "summary": {"type": "text"},
                    "fiscal_year": {"type": "keyword"},
                    "quarter": {"type": "keyword"},
                    "published_at": {"type": "date"},
                    "sentiment_score": {"type": "float"},
                    "sentiment_label": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "url": {"type": "keyword"},
                },
            },
        }
        client.indices.create(index=index_name, body=mapping)
        print(f"✅ Created OpenSearch index: {index_name}")
    else:
        print(f"✅ OpenSearch index already exists: {index_name}")


def index_document(doc_id: str, document: dict):
    """Index a document in OpenSearch."""
    client = get_opensearch_client()
    client.index(
        index=settings.opensearch_index,
        id=doc_id,
        body=document,
    )


def search_documents(
    query: str,
    company_symbol: Optional[str] = None,
    document_type: Optional[str] = None,
    limit: int = 10,
) -> list:
    """
    Full-text keyword search over indexed documents.
    Supports filtering by company and document type.
    """
    must_clauses = [
        {
            "multi_match": {
                "query": query,
                "fields": ["title^3", "content", "summary^2", "company_name"],
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        }
    ]

    filter_clauses = []
    if company_symbol:
        filter_clauses.append({"term": {"company_symbol": company_symbol}})
    if document_type:
        filter_clauses.append({"term": {"document_type": document_type}})

    search_body = {
        "size": limit,
        "query": {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses,
            }
        },
        "highlight": {
            "fields": {
                "content": {"fragment_size": 200, "number_of_fragments": 3},
                "title": {},
            }
        },
    }

    client = get_opensearch_client()
    response = client.search(
        index=settings.opensearch_index,
        body=search_body,
    )

    results = []
    for hit in response["hits"]["hits"]:
        result = hit["_source"]
        result["_score"] = hit["_score"]
        result["_id"] = hit["_id"]
        if "highlight" in hit:
            result["_highlights"] = hit["highlight"]
        results.append(result)

    return results
