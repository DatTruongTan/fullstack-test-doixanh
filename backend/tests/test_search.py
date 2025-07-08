import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.infrastructure.repositories.task_repository import TaskRepository
from app.domain.models.task import Task, PriorityEnum

@pytest.fixture
def mock_es_search():
    """Mock the Elasticsearch search function"""
    with patch('app.infrastructure.repositories.task_repository.search_documents') as mock:
        yield mock

@pytest.fixture
def mock_index_document():
    """Mock the Elasticsearch index_document function"""
    with patch('app.infrastructure.repositories.task_repository.index_document') as mock:
        yield mock

@pytest.fixture
def mock_task_db():
    """Create a mock database session"""
    mock_db = MagicMock()
    return mock_db

def test_search_tasks_with_elasticsearch(mock_es_search, mock_task_db):
    """Test that search uses Elasticsearch properly"""
    # Set up mock Elasticsearch response
    mock_es_search.return_value = [
        {
            "id": 1,
            "title": "Test Task",
            "description": "This is a test task",
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "due_date": datetime.now().isoformat(),
            "priority": "high",
            "owner_id": 1
        }
    ]
    
    # Create task repository
    repo = TaskRepository(mock_task_db)
    
    # Search for tasks
    results = repo.search_tasks("Test Task", 1)
    
    # Verify Elasticsearch was called correctly
    mock_es_search.assert_called_once()
    args, kwargs = mock_es_search.call_args
    assert args[0] == "tasks"  # index name
    assert args[1] == "Test Task"  # query
    assert "title^3" in kwargs["fields"]  # title field should have boosted relevance
    
    # Check results
    assert len(results) == 1
    assert results[0].title == "Test Task"
    assert results[0].owner_id == 1
    
def test_search_tasks_with_fallback(mock_es_search, mock_task_db):
    """Test that search falls back to database when Elasticsearch fails"""
    # Make Elasticsearch search raise an exception
    mock_es_search.side_effect = Exception("Elasticsearch error")
    
    # Set up mock database response
    mock_task = Task(
        id=1, 
        title="Database Task", 
        description="Found in database", 
        owner_id=1,
        completed=False,
        created_at=datetime.now(),
        due_date=datetime.now(),
        priority=PriorityEnum.normal
    )
    mock_task_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_task]
    
    # Create task repository
    repo = TaskRepository(mock_task_db)
    
    # Search for tasks
    results = repo.search_tasks("Database Task", 1)
    
    # Verify Elasticsearch was called but failed
    mock_es_search.assert_called_once()
    
    # Check that we got results from database instead
    assert len(results) == 1
    assert results[0].title == "Database Task"
    
def test_reindex_all_tasks(mock_index_document, mock_task_db):
    """Test that reindex_all_tasks indexes all tasks in Elasticsearch"""
    # Set up mock database response
    mock_tasks = [
        Task(
            id=1, 
            title="Task 1", 
            description="First task", 
            owner_id=1,
            completed=False,
            created_at=datetime.now(),
            due_date=datetime.now(),
            priority=PriorityEnum.normal
        ),
        Task(
            id=2, 
            title="Task 2", 
            description="Second task", 
            owner_id=1,
            completed=False,
            created_at=datetime.now(),
            due_date=datetime.now(),
            priority=PriorityEnum.high
        )
    ]
    mock_task_db.query.return_value.all.return_value = mock_tasks
    
    # Create task repository
    repo = TaskRepository(mock_task_db)
    
    # Reindex all tasks
    count = repo.reindex_all_tasks()
    
    # Verify index_document was called for each task
    assert mock_index_document.call_count == 2
    assert count == 2 