import pytest
import os
from task_manager import Task, TaskManager


class TestTask:
    """Tests for the Task class."""
    
    def test_task_creation(self):
        """Test creating a basic task."""
        task = Task("Buy milk", "high")
        assert task.title == "Buy milk"
        assert task.priority == "high"
        assert task.completed is False
    
    def test_task_creation_default_priority(self):
        """Test that default priority is medium."""
        task = Task("Read book")
        assert task.priority == "medium"
    
    def test_task_invalid_priority(self):
        """Test that invalid priority raises error."""
        with pytest.raises(ValueError):
            Task("Bad task", "urgent")
    
    def test_task_mark_complete(self):
        """Test marking a task as complete."""
        task = Task("Finish homework")
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True
    
    def test_task_to_dict(self):
        """Test converting task to dictionary."""
        task = Task("Test task", "low", "2024-12-01")
        data = task.to_dict()
        assert data["title"] == "Test task"
        assert data["priority"] == "low"
        assert data["due_date"] == "2024-12-01"
        assert data["completed"] is False
    
    def test_task_from_dict(self):
        """Test creating task from dictionary."""
        data = {
            "title": "Restored task",
            "priority": "high",
            "due_date": None,
            "completed": True,
            "created_at": "2024-01-01T00:00:00"
        }
        task = Task.from_dict(data)
        assert task.title == "Restored task"
        assert task.priority == "high"
        assert task.completed is True


class TestTaskManager:
    """Tests for the TaskManager class."""
    
    @pytest.fixture
    def temp_manager(self, tmp_path):
        """Create a TaskManager with a temporary file."""
        test_file = tmp_path / "test_tasks.json"
        return TaskManager(str(test_file))
    
    def test_add_task(self, temp_manager):
        """Test adding a task."""
        task = temp_manager.add_task("New task", "high")
        assert task.title == "New task"
        assert len(temp_manager.tasks) == 1
    
    def test_add_empty_task(self, temp_manager):
        """Test that empty task title raises error."""
        with pytest.raises(ValueError):
            temp_manager.add_task("")
    
    def test_add_whitespace_task(self, temp_manager):
        """Test that whitespace-only title raises error."""
        with pytest.raises(ValueError):
            temp_manager.add_task("   ")
    
    def test_list_tasks(self, temp_manager):
        """Test listing all tasks."""
        temp_manager.add_task("Task 1")
        temp_manager.add_task("Task 2")
        tasks = temp_manager.list_tasks()
        assert len(tasks) == 2
    
    def test_list_tasks_hide_completed(self, temp_manager):
        """Test listing only incomplete tasks."""
        temp_manager.add_task("Task 1")
        temp_manager.add_task("Task 2")
        temp_manager.complete_task(0)
        
        incomplete = temp_manager.list_tasks(show_completed=False)
        assert len(incomplete) == 1
        assert incomplete[0].title == "Task 2"
    
    def test_complete_task(self, temp_manager):
        """Test completing a task."""
        temp_manager.add_task("Task to complete")
        result = temp_manager.complete_task(0)
        assert result is True
        assert temp_manager.tasks[0].completed is True
    
    def test_complete_invalid_index(self, temp_manager):
        """Test completing task with invalid index."""
        temp_manager.add_task("Task 1")
        result = temp_manager.complete_task(5)
        assert result is False
    
    def test_delete_task(self, temp_manager):
        """Test deleting a task."""
        temp_manager.add_task("Task to delete")
        deleted = temp_manager.delete_task(0)
        assert deleted is not None
        assert deleted.title == "Task to delete"
        assert len(temp_manager.tasks) == 0
    
    def test_delete_invalid_index(self, temp_manager):
        """Test deleting with invalid index."""
        result = temp_manager.delete_task(0)
        assert result is None
    
    def test_save_and_load(self, tmp_path):
        """Test saving and loading tasks."""
        test_file = tmp_path / "test_tasks.json"
        
        # Create manager and add tasks
        manager1 = TaskManager(str(test_file))
        manager1.add_task("Persistent task", "high")
        
        # Create new manager with same file
        manager2 = TaskManager(str(test_file))
        assert len(manager2.tasks) == 1
        assert manager2.tasks[0].title == "Persistent task"
        assert manager2.tasks[0].priority == "high"
    
    def test_load_nonexistent_file(self, tmp_path):
        """Test loading when file doesn't exist."""
        test_file = tmp_path / "nonexistent.json"
        manager = TaskManager(str(test_file))
        assert len(manager.tasks) == 0
    
    def test_list_tasks_filter_by_priority(self, temp_manager):
        """Test filtering tasks by priority."""
        temp_manager.add_task("High priority task", "high")
        temp_manager.add_task("Medium priority task", "medium")
        temp_manager.add_task("Low priority task", "low")
        
        high_tasks = temp_manager.list_tasks(priority_filter="high")
        assert len(high_tasks) == 1
        assert high_tasks[0].priority == "high"
    
    def test_get_tasks_sorted(self, temp_manager):
        """Test that tasks are sorted by completion and priority."""
        temp_manager.add_task("Low task", "low")
        temp_manager.add_task("High task", "high")
        temp_manager.add_task("Medium task", "medium")
        temp_manager.complete_task(1)  # Complete the high task
        
        sorted_tasks = temp_manager.get_tasks_sorted()
        
        # First two should be incomplete (high and medium priority)
        assert not sorted_tasks[0].completed
        assert sorted_tasks[0].priority == "medium"
        assert not sorted_tasks[1].completed
        assert sorted_tasks[1].priority == "low"
        
        # Last should be completed
        assert sorted_tasks[2].completed
    
    def test_update_task_title(self, temp_manager):
        """Test updating a task's title."""
        temp_manager.add_task("Original title")
        updated = temp_manager.update_task(0, title="New title")
        assert updated.title == "New title"
    
    def test_update_task_priority(self, temp_manager):
        """Test updating a task's priority."""
        temp_manager.add_task("Task", "low")
        updated = temp_manager.update_task(0, priority="high")
        assert updated.priority == "high"
    
    def test_update_task_invalid_priority(self, temp_manager):
        """Test that updating with invalid priority raises error."""
        temp_manager.add_task("Task")
        with pytest.raises(ValueError):
            temp_manager.update_task(0, priority="urgent")
    
    def test_update_task_due_date(self, temp_manager):
        """Test updating a task's due date."""
        temp_manager.add_task("Task")
        updated = temp_manager.update_task(0, due_date="2024-12-31")
        assert updated.due_date == "2024-12-31"
    
    def test_update_invalid_index(self, temp_manager):
        """Test updating with invalid index returns None."""
        result = temp_manager.update_task(99, title="New title")
        assert result is None
    
    def test_get_statistics_empty(self, temp_manager):
        """Test statistics with no tasks."""
        stats = temp_manager.get_statistics()
        assert stats["total"] == 0
        assert stats["completed"] == 0
        assert stats["incomplete"] == 0
    
    def test_get_statistics(self, temp_manager):
        """Test statistics calculation."""
        temp_manager.add_task("Task 1", "high")
        temp_manager.add_task("Task 2", "medium")
        temp_manager.add_task("Task 3", "low")
        temp_manager.complete_task(0)
        
        stats = temp_manager.get_statistics()
        assert stats["total"] == 3
        assert stats["completed"] == 1
        assert stats["incomplete"] == 2
        assert stats["by_priority"]["high"] == 0  # Completed
        assert stats["by_priority"]["medium"] == 1
        assert stats["by_priority"]["low"] == 1