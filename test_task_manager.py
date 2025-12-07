import pytest
import os
from datetime import date, timedelta
from task_manager import Task, TaskManager, parse_date


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
            "tags": ["work", "urgent"],
            "completed": True,
            "created_at": "2024-01-01T00:00:00"
        }
        task = Task.from_dict(data)
        assert task.title == "Restored task"
        assert task.priority == "high"
        assert task.completed is True
        assert task.tags == ["work", "urgent"]
    
    def test_task_is_overdue(self):
        """Test overdue detection."""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        task = Task("Overdue task", due_date=yesterday)
        assert task.is_overdue() is True
    
    def test_task_not_overdue_future(self):
        """Test that future dates aren't overdue."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        task = Task("Future task", due_date=tomorrow)
        assert task.is_overdue() is False
    
    def test_task_not_overdue_completed(self):
        """Test that completed tasks aren't considered overdue."""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        task = Task("Old task", due_date=yesterday)
        task.mark_complete()
        assert task.is_overdue() is False
    
    def test_task_add_tag(self):
        """Test adding a tag to a task."""
        task = Task("Tagged task")
        task.add_tag("work")
        assert "work" in task.tags
    
    def test_task_add_duplicate_tag(self):
        """Test that duplicate tags aren't added."""
        task = Task("Tagged task")
        task.add_tag("work")
        task.add_tag("work")
        assert task.tags.count("work") == 1
    
    def test_task_remove_tag(self):
        """Test removing a tag from a task."""
        task = Task("Tagged task", tags=["work", "urgent"])
        task.remove_tag("work")
        assert "work" not in task.tags
        assert "urgent" in task.tags
    
    def test_task_tags_case_insensitive(self):
        """Test that tags are stored in lowercase."""
        task = Task("Task")
        task.add_tag("WORK")
        assert task.tags == ["work"]


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
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        
        temp_manager.add_task("Task 1", "high")
        temp_manager.add_task("Task 2", "medium", yesterday)  # Overdue
        temp_manager.add_task("Task 3", "low", tags=["work"])
        temp_manager.complete_task(0)
        
        stats = temp_manager.get_statistics()
        assert stats["total"] == 3
        assert stats["completed"] == 1
        assert stats["incomplete"] == 2
        assert stats["overdue"] == 1  # Task 2 is overdue
        assert stats["by_priority"]["high"] == 0  # Completed
        assert stats["by_priority"]["medium"] == 1
        assert stats["by_priority"]["low"] == 1
        assert "work" in stats["tags"]
    
    def test_search_tasks_by_title(self, temp_manager):
        """Test searching tasks by title."""
        temp_manager.add_task("Buy milk")
        temp_manager.add_task("Buy groceries")
        temp_manager.add_task("Meeting")
        
        results = temp_manager.search_tasks("buy")
        assert len(results) == 2
        assert all("buy" in t.title.lower() for t in results)
    
    def test_search_tasks_by_tag(self, temp_manager):
        """Test searching tasks by tag."""
        temp_manager.add_task("Task 1", tags=["work"])
        temp_manager.add_task("Task 2", tags=["personal"])
        temp_manager.add_task("Task 3", tags=["work", "urgent"])
        
        results = temp_manager.search_tasks("work")
        assert len(results) == 2
    
    def test_search_tasks_case_insensitive(self, temp_manager):
        """Test that search is case insensitive."""
        temp_manager.add_task("Important Meeting")
        
        results = temp_manager.search_tasks("important")
        assert len(results) == 1
    
    def test_get_tasks_by_tag(self, temp_manager):
        """Test filtering tasks by tag."""
        temp_manager.add_task("Task 1", tags=["work"])
        temp_manager.add_task("Task 2", tags=["personal"])
        temp_manager.add_task("Task 3", tags=["work"])
        
        work_tasks = temp_manager.get_tasks_by_tag("work")
        assert len(work_tasks) == 2
    
    def test_get_all_tags(self, temp_manager):
        """Test getting all unique tags."""
        temp_manager.add_task("Task 1", tags=["work", "urgent"])
        temp_manager.add_task("Task 2", tags=["personal"])
        temp_manager.add_task("Task 3", tags=["work"])
        
        all_tags = temp_manager.get_all_tags()
        assert len(all_tags) == 3
        assert "work" in all_tags
        assert "urgent" in all_tags
        assert "personal" in all_tags
    
    def test_list_tasks_filter_by_tag(self, temp_manager):
        """Test filtering task list by tag."""
        temp_manager.add_task("Task 1", tags=["work"])
        temp_manager.add_task("Task 2", tags=["personal"])
        
        work_tasks = temp_manager.list_tasks(tag_filter="work")
        assert len(work_tasks) == 1
        assert work_tasks[0].title == "Task 1"
    
    def test_add_tag_to_task(self, temp_manager):
        """Test adding a tag to an existing task."""
        temp_manager.add_task("Task")
        result = temp_manager.add_tag_to_task(0, "urgent")
        assert result is True
        assert "urgent" in temp_manager.tasks[0].tags
    
    def test_remove_tag_from_task(self, temp_manager):
        """Test removing a tag from a task."""
        temp_manager.add_task("Task", tags=["work", "urgent"])
        result = temp_manager.remove_tag_from_task(0, "urgent")
        assert result is True
        assert "urgent" not in temp_manager.tasks[0].tags
        assert "work" in temp_manager.tasks[0].tags
    
    def test_update_task_with_tags(self, temp_manager):
        """Test updating a task's tags."""
        temp_manager.add_task("Task", tags=["old"])
        updated = temp_manager.update_task(0, tags=["new", "fresh"])
        assert updated.tags == ["new", "fresh"]
    
    def test_add_task_with_natural_date(self, temp_manager):
        """Test adding task with natural language date."""
        # This will use the parse_date function
        task = temp_manager.add_task("Meeting", due_date="tomorrow")
        expected = (date.today() + timedelta(days=1)).isoformat()
        assert task.due_date == expected
    
    def test_clear_completed(self, temp_manager):
        """Test clearing only completed tasks."""
        temp_manager.add_task("Task 1")
        temp_manager.add_task("Task 2")
        temp_manager.add_task("Task 3")
        temp_manager.complete_task(0)
        temp_manager.complete_task(1)
        
        count = temp_manager.clear_completed()
        assert count == 2
        assert len(temp_manager.tasks) == 1
        assert temp_manager.tasks[0].title == "Task 3"
    
    def test_clear_completed_none(self, temp_manager):
        """Test clearing when no tasks are completed."""
        temp_manager.add_task("Task 1")
        temp_manager.add_task("Task 2")
        
        count = temp_manager.clear_completed()
        assert count == 0
        assert len(temp_manager.tasks) == 2
    
    def test_clear_all(self, temp_manager):
        """Test clearing all tasks."""
        temp_manager.add_task("Task 1")
        temp_manager.add_task("Task 2")
        temp_manager.add_task("Task 3")
        
        count = temp_manager.clear_all()
        assert count == 3
        assert len(temp_manager.tasks) == 0
    
    def test_clear_all_empty(self, temp_manager):
        """Test clearing when list is already empty."""
        count = temp_manager.clear_all()
        assert count == 0
        assert len(temp_manager.tasks) == 0