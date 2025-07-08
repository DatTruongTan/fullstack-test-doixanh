from fastapi import APIRouter, Depends, status
from typing import List

from app.application.schemas.task import Task, TaskCreate, TaskUpdate
from app.domain.models.user import User
from app.presentation.dependencies import get_current_active_user, get_task_service, is_admin
from app.application.services.task_service import TaskService

router = APIRouter()

def convert_enum_to_string(task):
    """Convert priority enum to string if needed"""
    if task and hasattr(task, 'priority') and hasattr(task.priority, 'value'):
        task.priority = task.priority.value
    return task

def convert_task_list(tasks):
    """Convert priority enum to string for a list of tasks"""
    return [convert_enum_to_string(task) for task in tasks]

@router.get("/", response_model=List[Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    task_service: TaskService = Depends(get_task_service),
):
    tasks = task_service.get_tasks(owner_id=current_user.id, skip=skip, limit=limit)
    return convert_task_list(tasks)

@router.post("/", response_model=Task)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    task_service: TaskService = Depends(get_task_service),
):
    db_task = task_service.create_task(task=task, owner_id=current_user.id)
    return convert_enum_to_string(db_task)

@router.get("/search/", response_model=List[Task])
def search_tasks_endpoint(
    query: str,
    current_user: User = Depends(get_current_active_user),
    task_service: TaskService = Depends(get_task_service),
):
    tasks = task_service.search_tasks(query=query, owner_id=current_user.id)
    return convert_task_list(tasks)

@router.get("/reindex", response_model=dict)
def reindex_tasks(
    current_user: User = Depends(is_admin),  # Only admins can reindex
    task_service: TaskService = Depends(get_task_service),
):
    """
    Reindex all tasks in Elasticsearch.
    This endpoint is admin-only and can be used to rebuild the search index.
    """
    count = task_service.reindex_all_tasks()
    return {"message": f"Successfully reindexed {count} tasks"}

@router.get("/{task_id}", response_model=Task)
def read_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    task_service: TaskService = Depends(get_task_service),
):
    db_task = task_service.get_task(task_id=task_id, owner_id=current_user.id)
    return convert_enum_to_string(db_task)

@router.put("/{task_id}", response_model=Task)
def update_task_endpoint(
    task_id: int,
    task: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    task_service: TaskService = Depends(get_task_service),
):
    db_task = task_service.update_task(task_id=task_id, task=task, owner_id=current_user.id)
    return convert_enum_to_string(db_task)

@router.delete("/{task_id}", response_model=Task)
def delete_task_endpoint(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    task_service: TaskService = Depends(get_task_service),
):
    db_task = task_service.delete_task(task_id=task_id, owner_id=current_user.id)
    return convert_enum_to_string(db_task) 