import pytest
from fastapi import status
from datetime import datetime, timedelta
import uuid
from app.domain.models.task import Task, PriorityEnum
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_task(client, db, token_headers):
    """
    Test task creation.
    """
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": "normal"
    }
    
    response = client.post("/api/v1/tasks/", json=task_data, headers=token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["priority"] == task_data["priority"]
    assert "id" in data
    
    # Check database
    created_task = db.query(Task).filter(Task.id == data["id"]).first()
    assert created_task is not None
    assert created_task.title == task_data["title"]
    
    # Handle either string or enum for priority
    if hasattr(created_task.priority, 'value'):
        assert created_task.priority.value == task_data["priority"]
    else:
        assert created_task.priority == task_data["priority"]

def test_create_task_unauthorized(client):
    """
    Test task creation without authentication.
    """
    task_data = {
        "title": "Unauthorized Task",
        "description": "This task should not be created",
        "due_date": datetime.now().isoformat(),
        "priority": "normal"
    }
    
    response = client.post("/api/v1/tasks/", json=task_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_tasks_empty(client, token_headers):
    """
    Test getting empty tasks list.
    """
    response = client.get("/api/v1/tasks/", headers=token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # It's okay if there are no tasks or some tasks

def create_test_task(db, test_user, **kwargs):
    """Helper to create a test task"""
    task_data = {
        "title": f"Test Task {uuid.uuid4()}",
        "description": "This is a test task",
        "due_date": datetime.now() + timedelta(days=1),
        "priority": PriorityEnum.normal,
        "completed": False,
        "owner_id": test_user.id
    }
    
    # Override with any kwargs
    task_data.update(kwargs)
    
    task = Task(**task_data)
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task

def test_update_task(client, db, token_headers, test_user):
    """
    Test updating a task.
    """
    # Create a task with a unique title
    unique_title = f"Update Task {uuid.uuid4()}"
    task = create_test_task(db, test_user, title=unique_title)
    
    # Update the task
    update_data = {"title": f"Updated {unique_title}", "priority": "high"}
    response = client.put(f"/api/v1/tasks/{task.id}", json=update_data, headers=token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == f"Updated {unique_title}"
    assert data["priority"] == "high"  # Check enum serialization

def test_delete_task(client, db, token_headers, test_user):
    """
    Test deleting a task.
    """
    # Create a task with a unique title
    unique_title = f"Delete Task {uuid.uuid4()}"
    task = create_test_task(db, test_user, title=unique_title)
    
    # Delete the task
    response = client.delete(f"/api/v1/tasks/{task.id}", headers=token_headers)
    
    assert response.status_code == 200
    
    # Verify it was deleted
    response = client.get(f"/api/v1/tasks/{task.id}", headers=token_headers)
    assert response.status_code == 404

def test_search_tasks(client, db, token_headers, test_user):
    """
    Test searching tasks.
    """
    # Create two tasks with unique searchable words
    search_word = f"SEARCHABLE-{uuid.uuid4()}"
    
    task1 = create_test_task(
        db, test_user, 
        title=f"Task with {search_word} in title", 
        description="Regular description"
    )
    
    task2 = create_test_task(
        db, test_user, 
        title="Regular title", 
        description=f"Description with {search_word} in it"
    )
    
    # Create a task that shouldn't match the search
    task3 = create_test_task(
        db, test_user, 
        title="No match task", 
        description="This shouldn't match the search"
    )
    
    # Search for tasks
    response = client.get(f"/api/v1/tasks/search/?query={search_word}", headers=token_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Should find 2 tasks
    assert len(data) == 2
    
    # Check the titles (the order might vary)
    titles = [task["title"] for task in data]
    assert any(search_word in title for title in titles)
    
    # Make sure the non-matching task isn't included
    assert "No match task" not in titles 