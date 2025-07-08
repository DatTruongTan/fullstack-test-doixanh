import pytest
from unittest.mock import MagicMock
from datetime import datetime
from fastapi import HTTPException

from app.application.services.task_service import TaskService
from app.application.services.auth_service import AuthService
from app.application.schemas.task import TaskCreate, TaskUpdate
from app.application.schemas.user import UserCreate
from app.domain.models.task import Task, PriorityEnum

class TestTaskService:
    def test_create_task(self):
        # Arrange
        mock_repo = MagicMock()
        task_service = TaskService(mock_repo)
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description",
            priority="normal",
            due_date=datetime.now()
        )
        owner_id = 1
        
        # Mock the create_task method of the repository
        expected_task = Task(id=1, title="Test Task", description="Test Description")
        mock_repo.create_task.return_value = expected_task
        
        # Act
        result = task_service.create_task(task_data, owner_id)
        
        # Assert
        assert result == expected_task
        mock_repo.create_task.assert_called_once_with(task_data, owner_id)
        
    def test_get_task_found(self):
        # Arrange
        mock_repo = MagicMock()
        task_service = TaskService(mock_repo)
        task_id = 1
        owner_id = 1
        
        # Mock the get_task method of the repository
        expected_task = Task(id=task_id, owner_id=owner_id)
        mock_repo.get_task.return_value = expected_task
        
        # Act
        result = task_service.get_task(task_id, owner_id)
        
        # Assert
        assert result == expected_task
        mock_repo.get_task.assert_called_once_with(task_id)
        
    def test_get_task_not_found(self):
        # Arrange
        mock_repo = MagicMock()
        task_service = TaskService(mock_repo)
        task_id = 1
        owner_id = 1
        
        # Mock the get_task method of the repository to return None
        mock_repo.get_task.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            task_service.get_task(task_id, owner_id)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in str(exc_info.value.detail)
        mock_repo.get_task.assert_called_once_with(task_id)
        
    def test_get_task_wrong_owner(self):
        # Arrange
        mock_repo = MagicMock()
        task_service = TaskService(mock_repo)
        task_id = 1
        owner_id = 1
        
        # Mock the get_task method of the repository to return a task with different owner
        task = Task(id=task_id, owner_id=2)  # Different owner_id
        mock_repo.get_task.return_value = task
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            task_service.get_task(task_id, owner_id)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in str(exc_info.value.detail)
        mock_repo.get_task.assert_called_once_with(task_id)
        
    def test_update_task(self):
        # Arrange
        mock_repo = MagicMock()
        task_service = TaskService(mock_repo)
        task_id = 1
        owner_id = 1
        update_data = TaskUpdate(title="Updated Title")
        
        # Mock the update_task method of the repository
        expected_updated_task = Task(id=task_id, title="Updated Title")
        mock_repo.update_task.return_value = expected_updated_task
        
        # Act
        result = task_service.update_task(task_id, update_data, owner_id)
        
        # Assert
        assert result == expected_updated_task
        mock_repo.update_task.assert_called_once_with(task_id, update_data, owner_id)
        
    def test_delete_task(self):
        # Arrange
        mock_repo = MagicMock()
        task_service = TaskService(mock_repo)
        task_id = 1
        owner_id = 1
        
        # Mock the delete_task method of the repository
        expected_deleted_task = Task(id=task_id)
        mock_repo.delete_task.return_value = expected_deleted_task
        
        # Act
        result = task_service.delete_task(task_id, owner_id)
        
        # Assert
        assert result == expected_deleted_task
        mock_repo.delete_task.assert_called_once_with(task_id, owner_id)

class TestAuthService:
    def test_register_user_success(self):
        # Arrange
        mock_repo = MagicMock()
        auth_service = AuthService(mock_repo)
        user_create = UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        
        # Mock the get_user_by_email and get_user_by_username methods to return None (user doesn't exist)
        mock_repo.get_user_by_email.return_value = None
        mock_repo.get_user_by_username.return_value = None
        
        # Mock the create_user method
        expected_user = MagicMock()
        expected_user.email = user_create.email
        expected_user.username = user_create.username
        mock_repo.create_user.return_value = expected_user
        
        # Act
        result = auth_service.register_user(user_create)
        
        # Assert
        assert result == expected_user
        mock_repo.get_user_by_email.assert_called_once_with(email=user_create.email)
        mock_repo.get_user_by_username.assert_called_once_with(username=user_create.username)
        mock_repo.create_user.assert_called_once_with(user=user_create)
        
    def test_login_user_success(self):
        # Arrange
        mock_repo = MagicMock()
        auth_service = AuthService(mock_repo)
        username = "testuser"
        password = "password123"
        
        # Mock the authenticate_user method to return a user
        expected_user = MagicMock()
        mock_repo.authenticate_user.return_value = expected_user
        
        # Act
        result = auth_service.login_user(username, password)
        
        # Assert
        assert result == expected_user
        mock_repo.authenticate_user.assert_called_once_with(username, password)
        
    def test_login_user_invalid_credentials(self):
        # Arrange
        mock_repo = MagicMock()
        auth_service = AuthService(mock_repo)
        username = "testuser"
        password = "wrongpassword"
        
        # Mock the authenticate_user method to return None (invalid credentials)
        mock_repo.authenticate_user.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login_user(username, password)
        
        assert exc_info.value.status_code == 401
        assert "Incorrect username or password" in str(exc_info.value.detail)
        mock_repo.authenticate_user.assert_called_once_with(username, password) 