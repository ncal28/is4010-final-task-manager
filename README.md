# Task Manager CLI

A powerful, colorful command-line task manager built with Python. Features smart date parsing, tagging system, and advanced search capabilities—all from your terminal.

![Tests](https://github.com/YOUR-USERNAME/YOUR-REPO/actions/workflows/tests.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)

## Features

- ✅ **Smart date parsing** - Use natural language like "tomorrow", "next friday", or "dec 15"
- ✅ **Tag system** - Organize tasks with custom tags (#work, #personal, etc.)
- ✅ **Search functionality** - Find tasks by keyword or tag
- ✅ **Bulk operations** - Clear completed tasks or start fresh
- ✅ **Priority management** - Set tasks as low, medium, or high priority
- ✅ **Overdue warnings** - Automatically highlights past-due tasks
- ✅ **Advanced filtering** - Filter by priority, tag, or completion status
- ✅ **Colorful output** - Beautiful terminal UI with priority colors
- ✅ **Automatic sorting** - Tasks sorted by priority and overdue status
- ✅ **Persistent storage** - All tasks saved automatically in JSON
- ✅ **Comprehensive statistics** - Track your productivity

## Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
   cd YOUR-REPO
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Add a Task

```bash
# Basic task with default medium priority
python task_manager.py add "Buy groceries"

# Task with high priority
python task_manager.py add "Complete final project" -p high

# Task with smart date parsing
python task_manager.py add "Team meeting" -d tomorrow -p high
python task_manager.py add "Project deadline" -d "next friday" -p high
python task_manager.py add "Doctor appointment" -d "dec 15" -p medium

# Task with tags
python task_manager.py add "Review PR" --tags work,code-review
python task_manager.py add "Grocery shopping" --tags personal,errands -p low

# Combine everything
python task_manager.py add "Submit assignment" -p high -d tomorrow --tags school,urgent
```

**Smart Date Examples:**
- `tomorrow`, `today`, `yesterday`
- `next monday`, `this friday`
- `in 3 days`, `in 2 weeks`
- `dec 15`, `december 25`
- `2024-12-31` (ISO format also works)

### List Tasks

```bash
# List all tasks
python task_manager.py list

# List only incomplete tasks
python task_manager.py list --hide-completed

# Filter by priority
python task_manager.py list -p high

# Filter by tag
python task_manager.py list -t work
```

**Example output:**
```
==================================================
Your Tasks
==================================================

0. [ ] ● Complete final project (due: 2024-12-08) #school #urgent
1. [✓] ◐ Team meeting #work
2. [ ] ● Project deadline ⚠ OVERDUE: 2024-12-01 #work
3. [ ] ○ Buy groceries #personal #errands

Total: 4 | Completed: 1 | Incomplete: 3 | Overdue: 1
```

### Complete a Task

```bash
# Complete task at index 0
python task_manager.py complete 0
```

### Delete a Task

```bash
# Delete task at index 1
python task_manager.py delete 1
```

### Update a Task

```bash
# Update title
python task_manager.py update 0 -t "Finish final project"

# Update priority
python task_manager.py update 0 -p low

# Update due date (with natural language!)
python task_manager.py update 0 -d "next monday"

# Update tags
python task_manager.py update 0 --tags urgent,important

# Update multiple properties
python task_manager.py update 0 -t "New title" -p high -d tomorrow --tags work
```

### View Statistics

```bash
python task_manager.py stats
```

**Example output:**
```
==================================================
Task Statistics
==================================================

Total tasks:      8
Completed:        3
Incomplete:       5
Overdue:          2

By Priority (Incomplete):
  High:     2
  Medium:   2
  Low:      1

Tags in use: #work, #personal, #urgent, #school
```

### Search Tasks

```bash
# Search by keyword in title
python task_manager.py search meeting

# Search by tag
python task_manager.py search work
```

**Example output:**
```
==================================================
Search Results for 'meeting'
==================================================

2. [ ] ◐ Team meeting #work
5. [ ] ● Client meeting tomorrow #work #important

Found 2 task(s)
```

### Manage Tags

```bash
# List all tags with counts
python task_manager.py tags --list

# Add tag to a task
python task_manager.py tags 0 --add urgent

# Remove tag from a task
python task_manager.py tags 0 --remove work
```

### Clear Tasks in Bulk

```bash
# Clear all completed tasks (no confirmation needed)
python task_manager.py clear --completed

# Clear all tasks (requires confirmation)
python task_manager.py clear --all

# Clear all tasks without confirmation prompt
python task_manager.py clear --all --force
```

**⚠️ Warning:** `clear --all` permanently deletes all tasks. Use with caution!

## Priority Legend

- 🔴 **● High** - Urgent and important tasks (shown in red)
- 🟡 **◐ Medium** - Standard priority (shown in yellow, default)
- 🔵 **○ Low** - Can wait (shown in blue)

**Overdue tasks** are marked with ⚠ in red and automatically sorted to the top.

## Tag System

Tags help organize your tasks into categories:
- Tags are prefixed with `#` (e.g., `#work`, `#personal`)
- Automatically converted to lowercase
- Multiple tags per task supported
- Search and filter by tags
- View all tags with usage counts

## Testing

Run the test suite with pytest:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=task_manager
```

All tests run automatically via GitHub Actions on every push.

## Project Structure

```
task-manager/
├── .github/
│   └── workflows/
│       └── tests.yml          # CI/CD configuration
├── task_manager.py             # Main application (~400 lines)
├── test_task_manager.py        # Test suite (~40 tests)
├── requirements.txt            # Python dependencies
├── tasks.json                  # Task storage (created on first run)
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
├── AGENTS.md                   # AI usage documentation
└── README.md                   # This file
```

## Dependencies

- **Python 3.10+** - Core language
- **colorama** - Cross-platform terminal colors
- **dateparser** - Natural language date parsing
- **pytest** - Testing framework

## How It Works

Tasks are stored in a JSON file (`tasks.json`) that persists between sessions. Each task includes:
- Title
- Priority (low/medium/high)
- Due date (optional, ISO format)
- Tags (optional, list of strings)
- Completion status (boolean)
- Creation timestamp

**Smart Features:**
- Natural language dates are parsed into ISO format (YYYY-MM-DD)
- Tasks are automatically sorted: overdue → incomplete by priority → completed
- Overdue detection compares due dates against today's date
- Tags are case-insensitive and searchable

## AI-Assisted Development

This project was developed with assistance from AI tools including Claude. For details on how AI was used in the development process, see [AGENTS.md](AGENTS.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Enhancements

Potential features for future versions:
- ~~Search tasks by keyword~~ ✅ Implemented!
- ~~Smart date parsing~~ ✅ Implemented!
- ~~Task categories/tags~~ ✅ Implemented!
- Recurring tasks
- Export to CSV or other formats
- Undo last action
- Task notes/descriptions
- Sub-tasks or checklist items
- Custom sort orders

## Contributing

This is an educational project for IS4010. Suggestions and feedback are welcome!

---

**Made with ❤️ and Python**