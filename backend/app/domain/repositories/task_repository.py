from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.task import Task
from app.application.schemas.task import TaskCreate, TaskUpdate

class ITaskRepository(ABC):
    @abstractmethod
    def get_task(self, task_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    def get_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        pass

    @abstractmethod
    def get_user_tasks(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        pass

    @abstractmethod
    def create_task(self, task: TaskCreate, owner_id: int) -> Task:
        pass

    @abstractmethod
    def update_task(self, task_id: int, task: TaskUpdate, owner_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    def delete_task(self, task_id: int, owner_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    def search_tasks(self, query: str, user_id: int) -> List[Task]:
        pass

    @abstractmethod
    def reindex_all_tasks(self) -> int:
        pass 