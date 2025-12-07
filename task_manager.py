import json
import argparse
from datetime import datetime, date
from typing import List, Optional
from colorama import Fore, Style, init
import dateparser

# Initialize colorama
init(autoreset=True)


def parse_date(date_str: str) -> Optional[str]:
    """
    Parse a natural language date string into ISO format.
    
    Examples:
        "tomorrow" -> "2024-12-08"
        "next friday" -> "2024-12-13"
        "dec 15" -> "2024-12-15"
        "2024-12-25" -> "2024-12-25"
    
    Returns None if parsing fails.
    """
    if not date_str:
        return None
    
    try:
        # Try to parse the date
        parsed_date = dateparser.parse(
            date_str,
            settings={
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': datetime.now()
            }
        )
        
        if parsed_date:
            return parsed_date.date().isoformat()
        return None
    except Exception:
        return None


class Task:
    """Represents a single task with title, priority, status, and tags."""
    
    def __init__(self, title: str, priority: str = "medium", due_date: Optional[str] = None, tags: Optional[List[str]] = None):
        self.title = title
        self.priority = priority.lower()
        self.due_date = due_date
        self.tags = tags or []
        self.completed = False
        self.created_at = datetime.now().isoformat()
        
        # Validate priority
        if self.priority not in ["low", "medium", "high"]:
            raise ValueError("Priority must be 'low', 'medium', or 'high'")
    
    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True
    
    def is_overdue(self):
        """Check if task is overdue."""
        if not self.due_date or self.completed:
            return False
        try:
            due = datetime.fromisoformat(self.due_date).date()
            return due < date.today()
        except (ValueError, AttributeError):
            return False
    
    def add_tag(self, tag: str):
        """Add a tag to the task."""
        if tag and tag not in self.tags:
            self.tags.append(tag.lower())
    
    def remove_tag(self, tag: str):
        """Remove a tag from the task."""
        if tag in self.tags:
            self.tags.remove(tag.lower())
    
    def to_dict(self):
        """Convert task to dictionary for JSON storage."""
        return {
            "title": self.title,
            "priority": self.priority,
            "due_date": self.due_date,
            "tags": self.tags,
            "completed": self.completed,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create a Task from a dictionary."""
        task = cls(data["title"], data["priority"], data.get("due_date"), data.get("tags", []))
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
        
        # Format due date with overdue warning
        due_str = ""
        if self.due_date:
            if self.is_overdue():
                due_str = f" {Fore.RED}⚠ OVERDUE: {self.due_date}{Style.RESET_ALL}"
            else:
                due_str = f" (due: {self.due_date})"
        
        # Format tags
        tags_str = ""
        if self.tags:
            tag_display = " ".join([f"{Fore.CYAN}#{tag}{Style.RESET_ALL}" for tag in self.tags])
            tags_str = f" {tag_display}"
        
        return f"[{status}] {color}{symbol}{Style.RESET_ALL} {title_color}{self.title}{Style.RESET_ALL}{due_str}{tags_str}"


class TaskManager:
    """Manages a collection of tasks with save/load functionality."""
    
    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename
        self.tasks: List[Task] = []
        self.load_tasks()
    
    def add_task(self, title: str, priority: str = "medium", due_date: Optional[str] = None, tags: Optional[List[str]] = None):
        """Add a new task to the list."""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        
        # Parse the due date if provided
        parsed_due = parse_date(due_date) if due_date else None
        
        task = Task(title.strip(), priority, parsed_due, tags)
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by keyword in title or tags."""
        query_lower = query.lower()
        results = []
        
        for task in self.tasks:
            # Search in title
            if query_lower in task.title.lower():
                results.append(task)
            # Search in tags
            elif any(query_lower in tag for tag in task.tags):
                results.append(task)
        
        return results
    
    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """Get all tasks with a specific tag."""
        tag_lower = tag.lower()
        return [t for t in self.tasks if tag_lower in t.tags]
    
    def get_all_tags(self) -> List[str]:
        """Get a list of all unique tags used."""
        all_tags = set()
        for task in self.tasks:
            all_tags.update(task.tags)
        return sorted(list(all_tags))
    
    def list_tasks(self, show_completed: bool = True, priority_filter: Optional[str] = None, tag_filter: Optional[str] = None):
        """Return list of tasks with optional filtering."""
        tasks = self.tasks
        
        # Filter by completion status
        if not show_completed:
            tasks = [t for t in tasks if not t.completed]
        
        # Filter by priority
        if priority_filter:
            tasks = [t for t in tasks if t.priority == priority_filter.lower()]
        
        # Filter by tag
        if tag_filter:
            tasks = [t for t in tasks if tag_filter.lower() in t.tags]
        
        return tasks
    
    def get_tasks_sorted(self, show_completed: bool = True, priority_filter: Optional[str] = None, tag_filter: Optional[str] = None):
        """Return tasks sorted by priority (high to low) and completion status."""
        tasks = self.list_tasks(show_completed, priority_filter, tag_filter)
        
        # Sort: incomplete first, then by priority (high to low), then by overdue status
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: (t.completed, priority_order[t.priority], not t.is_overdue()))
    
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
    
    def clear_completed(self):
        """Remove all completed tasks."""
        original_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if not t.completed]
        deleted_count = original_count - len(self.tasks)
        if deleted_count > 0:
            self.save_tasks()
        return deleted_count
    
    def clear_all(self):
        """Remove all tasks."""
        count = len(self.tasks)
        self.tasks = []
        if count > 0:
            self.save_tasks()
        return count
    
    def update_task(self, index: int, title: Optional[str] = None, 
                    priority: Optional[str] = None, due_date: Optional[str] = None, 
                    tags: Optional[List[str]] = None):
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
                # Parse the new due date
                task.due_date = parse_date(due_date) if due_date else None
            if tags is not None:
                task.tags = [t.lower() for t in tags]
            self.save_tasks()
            return task
        return None
    
    def add_tag_to_task(self, index: int, tag: str):
        """Add a tag to a specific task."""
        if 0 <= index < len(self.tasks):
            self.tasks[index].add_tag(tag)
            self.save_tasks()
            return True
        return False
    
    def remove_tag_from_task(self, index: int, tag: str):
        """Remove a tag from a specific task."""
        if 0 <= index < len(self.tasks):
            self.tasks[index].remove_tag(tag)
            self.save_tasks()
            return True
        return False
    
    def get_statistics(self):
        """Return statistics about tasks."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        incomplete = total - completed
        overdue = sum(1 for t in self.tasks if t.is_overdue())
        
        by_priority = {
            "high": sum(1 for t in self.tasks if t.priority == "high" and not t.completed),
            "medium": sum(1 for t in self.tasks if t.priority == "medium" and not t.completed),
            "low": sum(1 for t in self.tasks if t.priority == "low" and not t.completed)
        }
        
        tags = self.get_all_tags()
        
        return {
            "total": total,
            "completed": completed,
            "incomplete": incomplete,
            "overdue": overdue,
            "by_priority": by_priority,
            "tags": tags
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
        # Parse tags from comma-separated string
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else None
        
        task = manager.add_task(args.title, args.priority, args.due, tags)
        
        # Show parsed date if different from input
        date_info = ""
        if args.due and task.due_date:
            if args.due != task.due_date:
                date_info = f" (parsed as {task.due_date})"
        
        print(f"{Fore.GREEN}✓ Task added:{Style.RESET_ALL} {task.title}{date_info}")
        
    except ValueError as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


def cmd_list(args, manager):
    """Handle 'list' command."""
    tasks = manager.get_tasks_sorted(
        show_completed=not args.hide_completed,
        priority_filter=args.priority,
        tag_filter=args.tag
    )
    
    if not tasks:
        print(f"{Fore.YELLOW}No tasks found.{Style.RESET_ALL}")
        return
    
    print_header("Your Tasks")
    for task in tasks:
        # Find the actual index in the full task list
        actual_index = manager.tasks.index(task)
        print(f"{actual_index}. {task}")
    
    # Show statistics
    if not args.priority and not args.tag:
        stats = manager.get_statistics()
        status_line = (f"\n{Fore.CYAN}Total:{Style.RESET_ALL} {stats['total']} | "
                      f"{Fore.GREEN}Completed:{Style.RESET_ALL} {stats['completed']} | "
                      f"{Fore.YELLOW}Incomplete:{Style.RESET_ALL} {stats['incomplete']}")
        
        if stats['overdue'] > 0:
            status_line += f" | {Fore.RED}Overdue:{Style.RESET_ALL} {stats['overdue']}"
        
        print(status_line)


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
        # Parse tags if provided
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else None
        
        task = manager.update_task(args.index, args.title, args.priority, args.due, tags)
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
    
    if stats['overdue'] > 0:
        print(f"{Fore.RED}Overdue:          {stats['overdue']}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}By Priority (Incomplete):{Style.RESET_ALL}")
    print(f"  {Fore.RED}High:{Style.RESET_ALL}     {stats['by_priority']['high']}")
    print(f"  {Fore.YELLOW}Medium:{Style.RESET_ALL}   {stats['by_priority']['medium']}")
    print(f"  {Fore.BLUE}Low:{Style.RESET_ALL}      {stats['by_priority']['low']}")
    
    if stats['tags']:
        print(f"\n{Fore.CYAN}Tags in use:{Style.RESET_ALL} {', '.join(f'#{t}' for t in stats['tags'])}")


def cmd_search(args, manager):
    """Handle 'search' command."""
    results = manager.search_tasks(args.query)
    
    if not results:
        print(f"{Fore.YELLOW}No tasks found matching '{args.query}'.{Style.RESET_ALL}")
        return
    
    print_header(f"Search Results for '{args.query}'")
    for i, task in enumerate(results):
        # Find the actual index in the full task list
        actual_index = manager.tasks.index(task)
        print(f"{actual_index}. {task}")
    
    print(f"\n{Fore.CYAN}Found {len(results)} task(s){Style.RESET_ALL}")


def cmd_tags(args, manager):
    """Handle 'tags' command."""
    if args.list:
        # List all tags with counts
        all_tags = manager.get_all_tags()
        if not all_tags:
            print(f"{Fore.YELLOW}No tags in use.{Style.RESET_ALL}")
            return
        
        print_header("All Tags")
        for tag in all_tags:
            count = len(manager.get_tasks_by_tag(tag))
            print(f"#{tag} ({count} task{'s' if count != 1 else ''})")
    
    elif args.add:
        # Add tag to task
        if manager.add_tag_to_task(args.index, args.add):
            print(f"{Fore.GREEN}✓ Tag '{args.add}' added to task {args.index}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Error: Invalid task index {args.index}{Style.RESET_ALL}")
    
    elif args.remove:
        # Remove tag from task
        if manager.remove_tag_from_task(args.index, args.remove):
            print(f"{Fore.GREEN}✓ Tag '{args.remove}' removed from task {args.index}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Error: Invalid task index {args.index}{Style.RESET_ALL}")


def cmd_clear(args, manager):
    """Handle 'clear' command."""
    if args.completed:
        # Clear only completed tasks
        count = manager.clear_completed()
        if count > 0:
            print(f"{Fore.GREEN}✓ Cleared {count} completed task{'s' if count != 1 else ''}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}No completed tasks to clear.{Style.RESET_ALL}")
    
    elif args.all:
        # Clear all tasks with confirmation
        if not manager.tasks:
            print(f"{Fore.YELLOW}No tasks to clear.{Style.RESET_ALL}")
            return
        
        # Show what will be deleted
        total = len(manager.tasks)
        print(f"{Fore.YELLOW}⚠  Warning: This will delete all {total} task{'s' if total != 1 else ''}!{Style.RESET_ALL}")
        
        # Ask for confirmation (unless --force flag is used)
        if not args.force:
            response = input(f"Type 'yes' to confirm: ").strip().lower()
            if response != 'yes':
                print(f"{Fore.CYAN}Cancelled. No tasks were deleted.{Style.RESET_ALL}")
                return
        
        count = manager.clear_all()
        print(f"{Fore.GREEN}✓ Cleared all {count} task{'s' if count != 1 else ''}{Style.RESET_ALL}")
    
    else:
        print(f"{Fore.RED}Error: Please specify --completed or --all{Style.RESET_ALL}")
        print(f"Examples:")
        print(f"  python task_manager.py clear --completed")
        print(f"  python task_manager.py clear --all")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="A simple and colorful CLI task manager with smart dates and tags",
        epilog="Example: python task_manager.py add 'Finish project' -p high -d tomorrow --tags work,urgent"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    parser_add = subparsers.add_parser('add', help='Add a new task')
    parser_add.add_argument('title', help='Task title')
    parser_add.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], 
                           default='medium', help='Task priority (default: medium)')
    parser_add.add_argument('-d', '--due', help='Due date (e.g., "tomorrow", "next friday", "dec 15")')
    parser_add.add_argument('--tags', help='Comma-separated tags (e.g., "work,urgent")')
    
    # List command
    parser_list = subparsers.add_parser('list', help='List all tasks')
    parser_list.add_argument('--hide-completed', action='store_true', 
                            help='Hide completed tasks')
    parser_list.add_argument('-p', '--priority', choices=['low', 'medium', 'high'],
                            help='Filter by priority')
    parser_list.add_argument('-t', '--tag', help='Filter by tag')
    
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
    parser_update.add_argument('-d', '--due', help='New due date (natural language)')
    parser_update.add_argument('--tags', help='New comma-separated tags')
    
    # Stats command
    parser_stats = subparsers.add_parser('stats', help='Show task statistics')
    
    # Search command
    parser_search = subparsers.add_parser('search', help='Search tasks by keyword')
    parser_search.add_argument('query', help='Search query')
    
    # Tags command
    parser_tags = subparsers.add_parser('tags', help='Manage tags')
    parser_tags.add_argument('--list', action='store_true', help='List all tags')
    parser_tags.add_argument('index', type=int, nargs='?', help='Task index')
    parser_tags.add_argument('--add', help='Add tag to task')
    parser_tags.add_argument('--remove', help='Remove tag from task')
    
    # Clear command
    parser_clear = subparsers.add_parser('clear', help='Clear tasks in bulk')
    parser_clear.add_argument('--completed', action='store_true', 
                             help='Clear all completed tasks')
    parser_clear.add_argument('--all', action='store_true',
                             help='Clear all tasks (requires confirmation)')
    parser_clear.add_argument('--force', action='store_true',
                             help='Skip confirmation prompt (use with --all)')
    
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
    elif args.command == 'search':
        cmd_search(args, manager)
    elif args.command == 'tags':
        cmd_tags(args, manager)
    elif args.command == 'clear':
        cmd_clear(args, manager)


if __name__ == "__main__":
    main()