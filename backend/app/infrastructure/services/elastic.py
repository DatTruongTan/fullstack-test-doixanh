from elasticsearch import Elasticsearch, NotFoundError
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import json

from app.config import settings

def get_elasticsearch_client():
    """Get Elasticsearch client with the current settings URL"""
    return Elasticsearch(settings.ELASTICSEARCH_URL)

# Get initial client
es_client = get_elasticsearch_client()

# Define index name constant
TASK_INDEX = "tasks"

def create_index(index_name: str, mappings: Dict[str, Any]) -> bool:

    if not es_client.indices.exists(index=index_name):
        es_client.indices.create(
            index=index_name,
            mappings=mappings
        )
        return True
    return False

def delete_index(index_name: str) -> bool:

    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)
        return True
    return False

def index_document(index_name: str, document_id: str, document: Dict[str, Any]) -> Dict[str, Any]:

    return es_client.index(
        index=index_name,
        id=document_id,
        document=document
    )

def get_document(index_name: str, document_id: str) -> Optional[Dict[str, Any]]:

    try:
        result = es_client.get(index=index_name, id=document_id)
        if result and result.get("found"):
            return result["_source"]
    except:
        return None
    return None

def delete_document(index_name: str, document_id: str) -> bool:

    try:
        result = es_client.delete(index=index_name, id=document_id)
        return result.get("result") == "deleted"
    except:
        return False

def search_documents(index_name: str, query: str, fields: List[str] = None, size: int = 100) -> List[Dict[str, Any]]:

    search_fields = fields or ["*"]
    query_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": search_fields,
                "type": "best_fields",
                "fuzziness": "AUTO"
            }
        },
        "size": size
    }

    result = es_client.search(
        index=index_name,
        body=query_body
    )

    hits = result.get("hits", {}).get("hits", [])
    return [hit["_source"] for hit in hits]

TASK_MAPPINGS = {
    "properties": {
        "id": {"type": "integer"},
        "title": {"type": "text", "analyzer": "standard"},
        "description": {"type": "text", "analyzer": "standard"},
        "completed": {"type": "boolean"},
        "created_at": {"type": "date"},
        "due_date": {"type": "date"},
        "priority": {"type": "keyword"},
        "owner_id": {"type": "integer"}
    }
}

def setup_elasticsearch():
    # Check if index exists before creating
    if not es_client.indices.exists(index=TASK_INDEX):
        create_index(TASK_INDEX, TASK_MAPPINGS)
    return True 