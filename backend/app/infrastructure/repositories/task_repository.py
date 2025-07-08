from sqlalchemy.orm import Session
import json
from datetime import datetime
import logging

from app.domain.models.task import Task, PriorityEnum
from app.application.schemas.task import TaskCreate, TaskUpdate
from app.infrastructure.services.elastic import (
    TASK_INDEX, index_document, search_documents, delete_document
)
from app.infrastructure.services.redis import get_cache, set_cache, delete_cache
from app.domain.repositories.task_repository import ITaskRepository

logger = logging.getLogger(__name__)

class TaskRepository(ITaskRepository):
    def __init__(self, db: Session):
        self.db = db
        
    def _serialize_task(self, task: Task) -> dict:
        """Serialize Task object to a dictionary for cache/ES storage.

        Args:
            task (Task): The task to serialize.

        Returns:
            dict: The serialized task.
        """
        task_dict = task.__dict__.copy()
        if "_sa_instance_state" in task_dict:
            task_dict.pop("_sa_instance_state")
        if "created_at" in task_dict and isinstance(task_dict["created_at"], datetime):
            task_dict["created_at"] = task_dict["created_at"].isoformat()
        if "due_date" in task_dict and isinstance(task_dict["due_date"], datetime):
            task_dict["due_date"] = task_dict["due_date"].isoformat()
        if "priority" in task_dict and isinstance(task_dict["priority"], PriorityEnum):
            task_dict["priority"] = task_dict["priority"].value
        return task_dict
    
    def _get_cache_key(self, key_type: str, **kwargs) -> str:
        """Generate consistent cache keys.

        Args:
            key_type (str): The type of key to generate.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The generated cache key.
        """
        if key_type == "task":
            return f"task:{kwargs['task_id']}"
        elif key_type == "all_tasks":
            return f"tasks:all:{kwargs['skip']}:{kwargs['limit']}"
        elif key_type == "user_tasks":
            return f"tasks:user:{kwargs['user_id']}:{kwargs['skip']}:{kwargs['limit']}"
        return f"tasks:{key_type}"
    
    def _index_task_to_elasticsearch(self, task: Task) -> None:
        """Index a task to Elasticsearch with error handling.

        Args:
            task (Task): The task to index.
        """
        try:
            task_dict = self._serialize_task(task)
            index_document(TASK_INDEX, str(task.id), task_dict)
        except Exception as e:
            logger.error(f"Failed to index task {task.id} in Elasticsearch: {str(e)}")

    def get_tasks(self, skip: int = 0, limit: int = 100) -> list[Task]:
        """Get all tasks from the database with pagination.

        Args:
            skip (int, optional): The number of tasks to skip. Defaults to 0.
            limit (int, optional): The number of tasks to return. Defaults to 100.

        Returns:
            list[Task]: A list of tasks.
        """
        cache_key = self._get_cache_key("all_tasks", skip=skip, limit=limit)
        cached_data = get_cache(cache_key)

        if cached_data:
            tasks_data = json.loads(cached_data)
            return [Task(**data) for data in tasks_data]

        tasks = self.db.query(Task).order_by(Task.due_date).offset(skip).limit(limit).all()

        tasks_data = []
        for task in tasks:
            tasks_data.append(self._serialize_task(task))

        set_cache(cache_key, json.dumps(tasks_data), 300)
        return tasks

    def create_task(self, task: TaskCreate, owner_id: int) -> Task:
        """Create a new task.

        Args:
            task (TaskCreate): The task to create.
            owner_id (int): The ID of the owner of the task.

        Returns:
            Task: The created task.
        """
        task_data = task.model_dump()
        db_task = Task(**task_data, owner_id=owner_id)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)

        # Index in Elasticsearch
        self._index_task_to_elasticsearch(db_task)

        return db_task

    def get_task(self, task_id: int) -> Task:
        """Get a task by its ID.

        Args:
            task_id (int): The ID of the task to get.

        Returns:
            Task: The task.
        """
        cache_key = self._get_cache_key("task", task_id=task_id)
        cached_data = get_cache(cache_key)
        if cached_data:
            return Task(**json.loads(cached_data))

        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task:
            task_dict = self._serialize_task(task)
            set_cache(cache_key, json.dumps(task_dict), 300)
        return task

    def update_task(self, task_id: int, task: TaskUpdate, owner_id: int) -> Task:
        """Update a task.

        Args:
            task_id (int): The ID of the task to update.
            task (TaskUpdate): The task to update.
            owner_id (int): The ID of the owner of the task.

        Returns:
            Task: The updated task.
        """
        db_task = self.db.query(Task).filter(
            Task.id == task_id, Task.owner_id == owner_id
        ).first()

        if db_task:
            task_data = task.model_dump(exclude_unset=True)
            for key, value in task_data.items():
                setattr(db_task, key, value)
            self.db.commit()
            self.db.refresh(db_task)
            
            self._index_task_to_elasticsearch(db_task)

            cache_key = self._get_cache_key("task", task_id=task_id)
            delete_cache(cache_key)
            
            return db_task
        return None

    def delete_task(self, task_id: int, owner_id: int) -> Task:
        """Delete a task.

        Args:
            task_id (int): The ID of the task to delete.
            owner_id (int): The ID of the owner of the task.

        Returns:
            Task: The deleted task.
        """
        db_task = self.db.query(Task).filter(
            Task.id == task_id, Task.owner_id == owner_id
        ).first()

        if db_task:
            self.db.delete(db_task)
            self.db.commit()
            
            try:
                delete_document(TASK_INDEX, str(task_id))
            except Exception as e:
                logger.error(f"Failed to delete task from Elasticsearch: {str(e)}")
                
            cache_key = self._get_cache_key("task", task_id=task_id)
            delete_cache(cache_key)
            
            return db_task
        return None

    def get_user_tasks(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Task]:
        """Get all tasks for a user with pagination.

        Args:
            user_id (int): The ID of the user to get tasks for.
            skip (int, optional): The number of tasks to skip. Defaults to 0.
            limit (int, optional): The number of tasks to return. Defaults to 100.

        Returns:
            list[Task]: A list of tasks.
        """
        cache_key = self._get_cache_key("user_tasks", user_id=user_id, skip=skip, limit=limit)
        cached_data = get_cache(cache_key)

        if cached_data:
            tasks_data = json.loads(cached_data)
            return [Task(**data) for data in tasks_data]

        tasks = self.db.query(Task).filter(Task.owner_id == user_id).order_by(Task.due_date).offset(skip).limit(limit).all()

        tasks_data = []
        for task in tasks:
            tasks_data.append(self._serialize_task(task))

        set_cache(cache_key, json.dumps(tasks_data), 300)
        return tasks

    def search_tasks(self, query: str, user_id: int) -> list[Task]:
        """Search tasks using Elasticsearch based on query and user_id.

        Args:
            query (str): The query to search for.
            user_id (int): The ID of the user to search for.

        Returns:
            list[Task]: A list of tasks.
        """
        try:
            # Try to search with Elasticsearch first
            search_results = search_documents(
                TASK_INDEX,
                query,
                fields=["title^3", "description"],  # Title is more important
                size=100
            )
            
            filtered_results = [result for result in search_results if result.get("owner_id") == user_id]
            
            if filtered_results:
                tasks = []
                for result in filtered_results:
                    if "created_at" in result and isinstance(result["created_at"], str):
                        result["created_at"] = datetime.fromisoformat(result["created_at"])
                    if "due_date" in result and isinstance(result["due_date"], str):
                        result["due_date"] = datetime.fromisoformat(result["due_date"])

                    if "priority" in result and not isinstance(result["priority"], PriorityEnum):
                        for enum_value in PriorityEnum:
                            if enum_value.value == result["priority"]:
                                result["priority"] = enum_value
                                break
                                
                    task = Task(**result)
                    tasks.append(task)

                tasks.sort(key=lambda t: t.due_date if t.due_date else datetime.max)
                return tasks
        except Exception as e:
            logger.error(f"Elasticsearch search failed: {str(e)}")
            
        logger.info(f"Falling back to database search for query: '{query}'")
        return self.db.query(Task).filter(
            Task.owner_id == user_id,
            Task.title.ilike(f"%{query}%") | Task.description.ilike(f"%{query}%")
        ).order_by(Task.due_date).all()
        
    def reindex_all_tasks(self) -> int:
        """Reindex all tasks in Elasticsearch.

        Returns:
            int: The number of tasks reindexed.
        """
        tasks = self.db.query(Task).all()
        count = 0
        
        for task in tasks:
            try:
                task_dict = self._serialize_task(task)
                index_document(TASK_INDEX, str(task.id), task_dict)
                count += 1
            except Exception as e:
                logger.error(f"Failed to index task {task.id}: {str(e)}")
                
        return count 