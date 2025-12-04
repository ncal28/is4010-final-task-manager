import json
import argparse
from datetime import datetime
from typing import List, Optional
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


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
        """Return a colored string representation of the task."""
        status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if self.completed else " "
        
        # Priority colors and symbols
        priority_display = {
            "low": (Fore.BLUE, "○"),
            "medium": (Fore.YELLOW, "◐"),
            "high": (Fore.RED, "●")
        }
        color, symbol = priority_display[self.priority]
        
        # Gray out completed tasks
        title_color = Fore.LIGHTBLACK_EX if self.completed else ""
        
        due_str = f" (due: {self.due_date})" if self.due_date else ""
        
        return f"[{status}] {color}{symbol}{Style.RESET_ALL} {title_color}{self.title}{Style.RESET_ALL}{due_str}"


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
    
    def list_tasks(self, show_completed: bool = True, priority_filter: Optional[str] = None):
        """Return list of tasks with optional filtering."""
        tasks = self.tasks
        
        # Filter by completion status
        if not show_completed:
            tasks = [t for t in tasks if not t.completed]
        
        # Filter by priority
        if priority_filter:
            tasks = [t for t in tasks if t.priority == priority_filter.lower()]
        
        return tasks
    
    def get_tasks_sorted(self, show_completed: bool = True, priority_filter: Optional[str] = None):
        """Return tasks sorted by priority (high to low) and completion status."""
        tasks = self.list_tasks(show_completed, priority_filter)
        
        # Sort: incomplete first, then by priority (high to low)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: (t.completed, priority_order[t.priority]))
    
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
    
    def update_task(self, index: int, title: Optional[str] = None, 
                    priority: Optional[str] = None, due_date: Optional[str] = None):
        """Update a task's properties."""
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            if title:
                task.title = title.strip()
            if priority:
                if priority.lower() not in ["low", "medium", "high"]:
                    raise ValueError("Priority must be 'low', 'medium', or 'high'")
                task.priority = priority.lower()
            if due_date is not None:
                task.due_date = due_date
            self.save_tasks()
            return task
        return None
    
    def get_statistics(self):
        """Return statistics about tasks."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        incomplete = total - completed
        
        by_priority = {
            "high": sum(1 for t in self.tasks if t.priority == "high" and not t.completed),
            "medium": sum(1 for t in self.tasks if t.priority == "medium" and not t.completed),
            "low": sum(1 for t in self.tasks if t.priority == "low" and not t.completed)
        }
        
        return {
            "total": total,
            "completed": completed,
            "incomplete": incomplete,
            "by_priority": by_priority
        }
    
    def save_tasks(self):
        """Save all tasks to JSON file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump([t.to_dict() for t in self.tasks], f, indent=2)
        except IOError as e:
            print(f"{Fore.RED}Error saving tasks: {e}{Style.RESET_ALL}")
    
    def load_tasks(self):
        """Load tasks from JSON file."""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(t) for t in data]
        except FileNotFoundError:
            self.tasks = []
        except json.JSONDecodeError:
            print(f"{Fore.YELLOW}Warning: Could not parse {self.filename}, starting fresh{Style.RESET_ALL}")
            self.tasks = []


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Fore.CYAN}{'=' * 50}")
    print(f"{text}")
    print(f"{'=' * 50}{Style.RESET_ALL}\n")


def cmd_add(args, manager):
    """Handle 'add' command."""
    try:
        task = manager.add_task(args.title, args.priority, args.due)
        print(f"{Fore.GREEN}✓ Task added:{Style.RESET_ALL} {task.title}")
    except ValueError as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


def cmd_list(args, manager):
    """Handle 'list' command."""
    tasks = manager.get_tasks_sorted(
        show_completed=not args.hide_completed,
        priority_filter=args.priority
    )
    
    if not tasks:
        print(f"{Fore.YELLOW}No tasks found.{Style.RESET_ALL}")
        return
    
    print_header("Your Tasks")
    for i, task in enumerate(tasks):
        print(f"{i}. {task}")
    
    # Show statistics
    if not args.priority:
        stats = manager.get_statistics()
        print(f"\n{Fore.CYAN}Total:{Style.RESET_ALL} {stats['total']} | "
              f"{Fore.GREEN}Completed:{Style.RESET_ALL} {stats['completed']} | "
              f"{Fore.YELLOW}Incomplete:{Style.RESET_ALL} {stats['incomplete']}")


def cmd_complete(args, manager):
    """Handle 'complete' command."""
    if manager.complete_task(args.index):
        print(f"{Fore.GREEN}✓ Task {args.index} marked as complete!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Error: Invalid task index {args.index}{Style.RESET_ALL}")


def cmd_delete(args, manager):
    """Handle 'delete' command."""
    deleted = manager.delete_task(args.index)
    if deleted:
        print(f"{Fore.GREEN}✓ Deleted:{Style.RESET_ALL} {deleted.title}")
    else:
        print(f"{Fore.RED}Error: Invalid task index {args.index}{Style.RESET_ALL}")


def cmd_update(args, manager):
    """Handle 'update' command."""
    try:
        task = manager.update_task(args.index, args.title, args.priority, args.due)
        if task:
            print(f"{Fore.GREEN}✓ Task updated:{Style.RESET_ALL} {task.title}")
        else:
            print(f"{Fore.RED}Error: Invalid task index {args.index}{Style.RESET_ALL}")
    except ValueError as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


def cmd_stats(args, manager):
    """Handle 'stats' command."""
    stats = manager.get_statistics()
    
    print_header("Task Statistics")
    print(f"Total tasks:      {stats['total']}")
    print(f"{Fore.GREEN}Completed:        {stats['completed']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Incomplete:       {stats['incomplete']}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}By Priority (Incomplete):{Style.RESET_ALL}")
    print(f"  {Fore.RED}High:{Style.RESET_ALL}     {stats['by_priority']['high']}")
    print(f"  {Fore.YELLOW}Medium:{Style.RESET_ALL}   {stats['by_priority']['medium']}")
    print(f"  {Fore.BLUE}Low:{Style.RESET_ALL}      {stats['by_priority']['low']}")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="A simple and colorful CLI task manager",
        epilog="Example: python task_manager.py add 'Finish project' -p high -d 2024-12-01"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    parser_add = subparsers.add_parser('add', help='Add a new task')
    parser_add.add_argument('title', help='Task title')
    parser_add.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], 
                           default='medium', help='Task priority (default: medium)')
    parser_add.add_argument('-d', '--due', help='Due date (e.g., 2024-12-01)')
    
    # List command
    parser_list = subparsers.add_parser('list', help='List all tasks')
    parser_list.add_argument('--hide-completed', action='store_true', 
                            help='Hide completed tasks')
    parser_list.add_argument('-p', '--priority', choices=['low', 'medium', 'high'],
                            help='Filter by priority')
    
    # Complete command
    parser_complete = subparsers.add_parser('complete', help='Mark a task as complete')
    parser_complete.add_argument('index', type=int, help='Task index')
    
    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete a task')
    parser_delete.add_argument('index', type=int, help='Task index')
    
    # Update command
    parser_update = subparsers.add_parser('update', help='Update a task')
    parser_update.add_argument('index', type=int, help='Task index')
    parser_update.add_argument('-t', '--title', help='New task title')
    parser_update.add_argument('-p', '--priority', choices=['low', 'medium', 'high'],
                              help='New priority')
    parser_update.add_argument('-d', '--due', help='New due date')
    
    # Stats command
    parser_stats = subparsers.add_parser('stats', help='Show task statistics')
    
    args = parser.parse_args()
    
    # If no command provided, show help
    if not args.command:
        parser.print_help()
        return
    
    # Create task manager
    manager = TaskManager()
    
    # Route to appropriate command handler
    if args.command == 'add':
        cmd_add(args, manager)
    elif args.command == 'list':
        cmd_list(args, manager)
    elif args.command == 'complete':
        cmd_complete(args, manager)
    elif args.command == 'delete':
        cmd_delete(args, manager)
    elif args.command == 'update':
        cmd_update(args, manager)
    elif args.command == 'stats':
        cmd_stats(args, manager)


if __name__ == "__main__":
    main()