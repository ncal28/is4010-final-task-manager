import json
from datetime import datetime
from typing import List, Optional

class Task:
    """Represents a single task with title, priority, and status."""
    
    def __init__(self, title: str, priority: str = "medium", due_date: Optional[str] = None):
        self.title = title
        self.priority = priority.lower()
        self.due_date = due_date
        self.completed = False
        self.created_at = datetime.now().isoformat()
        
        # Validate priority
        if self.priority not in ["low", "medium", "high"]:
            raise ValueError("Priority must be 'low', 'medium', or 'high'")
    
    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True
    
    def to_dict(self):
        """Convert task to dictionary for JSON storage."""
        return {
            "title": self.title,
            "priority": self.priority,
            "due_date": self.due_date,
            "completed": self.completed,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create a Task from a dictionary."""
        task = cls(data["title"], data["priority"], data.get("due_date"))
        task.completed = data["completed"]
        task.created_at = data["created_at"]
        return task
    
    def __str__(self):
        status = "✓" if self.completed else " "
        priority_symbol = {"low": "○", "medium": "◐", "high": "●"}
        return f"[{status}] {priority_symbol[self.priority]} {self.title}"


class TaskManager:
    """Manages a collection of tasks with save/load functionality."""
    
    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename
        self.tasks: List[Task] = []
        self.load_tasks()
    
    def add_task(self, title: str, priority: str = "medium", due_date: Optional[str] = None):
        """Add a new task to the list."""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        
        task = Task(title.strip(), priority, due_date)
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def list_tasks(self, show_completed: bool = True):
        """Return list of tasks, optionally filtering out completed ones."""
        if show_completed:
            return self.tasks
        return [t for t in self.tasks if not t.completed]
    
    def complete_task(self, index: int):
        """Mark a task as completed by its index."""
        if 0 <= index < len(self.tasks):
            self.tasks[index].mark_complete()
            self.save_tasks()
            return True
        return False
    
    def delete_task(self, index: int):
        """Delete a task by its index."""
        if 0 <= index < len(self.tasks):
            deleted = self.tasks.pop(index)
            self.save_tasks()
            return deleted
        return None
    
    def save_tasks(self):
        """Save all tasks to JSON file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump([t.to_dict() for t in self.tasks], f, indent=2)
        except IOError as e:
            print(f"Error saving tasks: {e}")
    
    def load_tasks(self):
        """Load tasks from JSON file."""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(t) for t in data]
        except FileNotFoundError:
            # File doesn't exist yet, start with empty list
            self.tasks = []
        except json.JSONDecodeError:
            print(f"Warning: Could not parse {self.filename}, starting fresh")
            self.tasks = []


def main():
    """Simple CLI interface for testing."""
    manager = TaskManager()
    
    print("Task Manager - Quick Test")
    print("-" * 40)
    
    # Add some tasks
    manager.add_task("Complete IS4010 final project", "high", "2024-12-01")
    manager.add_task("Study for exam", "medium")
    manager.add_task("Buy groceries", "low")
    
    # List all tasks
    print("\nAll tasks:")
    for i, task in enumerate(manager.list_tasks()):
        print(f"{i}. {task}")
    
    # Complete a task
    manager.complete_task(1)
    
    print("\nAfter completing task 1:")
    for i, task in enumerate(manager.list_tasks()):
        print(f"{i}. {task}")


if __name__ == "__main__":
    main()