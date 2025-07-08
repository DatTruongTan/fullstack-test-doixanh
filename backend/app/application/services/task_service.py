from fastapi import HTTPException
from app.domain.repositories.task_repository import ITaskRepository
from app.application.schemas.task import TaskCreate, TaskUpdate
from app.domain.models.task import Task

class TaskService:
    def __init__(self, task_repository: ITaskRepository):
        self.task_repository = task_repository

    def create_task(self, task: TaskCreate, owner_id: int) -> Task:
        """Create a new task.

        Args:
            task (TaskCreate): The task to create.
            owner_id (int): The ID of the owner of the task.

        Returns:
            Task: The created task.
        """
        return self.task_repository.create_task(task, owner_id)

    def get_task(self, task_id: int, owner_id: int) -> Task:
        """Get a task by its ID.

        Args:
            task_id (int): The ID of the task to get.
            owner_id (int): The ID of the owner of the task.

        Returns:
            Task: The task.
        """
        task = self.task_repository.get_task(task_id)
        if not task or task.owner_id != owner_id:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def get_tasks(self, owner_id: int, skip: int = 0, limit: int = 100) -> list[Task]:
        """Get all tasks for a user with pagination.

        Args:
            owner_id (int): The ID of the owner of the tasks to get.
            skip (int, optional): The number of tasks to skip. Defaults to 0.
            limit (int, optional): The number of tasks to return. Defaults to 100.

        Returns:
            list[Task]: A list of tasks.
        """
        return self.task_repository.get_user_tasks(owner_id, skip, limit)

    def update_task(self, task_id: int, task: TaskUpdate, owner_id: int) -> Task:
        """Update a task.

        Args:
            task_id (int): The ID of the task to update.
            task (TaskUpdate): The task to update.
            owner_id (int): The ID of the owner of the task.

        Returns:
            Task: The updated task.
        """
        updated_task = self.task_repository.update_task(task_id, task, owner_id)
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated_task

    def delete_task(self, task_id: int, owner_id: int) -> Task:
        """Delete a task.

        Args:
            task_id (int): The ID of the task to delete.
            owner_id (int): The ID of the owner of the task.

        Raises:
            HTTPException: If the task is not found.

        Returns:
            Task: The deleted task.
        """
        deleted_task = self.task_repository.delete_task(task_id, owner_id)
        if not deleted_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return deleted_task
    
    def search_tasks(self, query: str, owner_id: int) -> list[Task]:
        """Search tasks using Elasticsearch based on query and owner_id.

        Args:
            query (str): The query to search for.
            owner_id (int): The ID of the owner of the tasks to search for.

        Returns:
            list[Task]: A list of tasks.
        """
        return self.task_repository.search_tasks(query, owner_id)
        
    def reindex_all_tasks(self) -> int:
        """Reindex all tasks in Elasticsearch.

        Returns:
            int: The number of tasks reindexed.
        """
        return self.task_repository.reindex_all_tasks() 