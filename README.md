# is4010-final-task-manager
Final project for App Dev w/ AI, a command line task manager tool

# Task Manager CLI

A simple, colorful command-line task manager built with Python. Track your tasks with priorities, due dates, and completion status—all from your terminal.

![Tests](https://github.com/YOUR-USERNAME/YOUR-REPO/actions/workflows/tests.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)

## Features

- ✅ **Add tasks** with titles, priorities (low/medium/high), and due dates
- ✅ **List tasks** with filtering by priority and completion status
- ✅ **Complete tasks** to mark them as done
- ✅ **Delete tasks** you no longer need
- ✅ **Update tasks** to change title, priority, or due date
- ✅ **View statistics** about your tasks
- ✅ **Colorful output** for better readability
- ✅ **Automatic sorting** by priority and completion status
- ✅ **Persistent storage** using JSON files

## Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
   cd YOUR-REPO
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv/Scripts/activate
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

# Task with due date
python task_manager.py add "Submit assignment" -p high -d 2024-12-01
```

### List Tasks

```bash
# List all tasks
python task_manager.py list

# List only incomplete tasks
python task_manager.py list --hide-completed

# Filter by priority
python task_manager.py list -p high
```

**Example output:**
```
==================================================
Your Tasks
==================================================

0. [ ] ● Complete final project (due: 2024-12-01)
1. [ ] ◐ Submit assignment
2. [✓] ○ Buy groceries

Total: 3 | Completed: 1 | Incomplete: 2
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

# Update due date
python task_manager.py update 0 -d 2024-12-15

# Update multiple properties
python task_manager.py update 0 -t "New title" -p high -d 2024-12-01
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

Total tasks:      5
Completed:        2
Incomplete:       3

By Priority (Incomplete):
  High:     1
  Medium:   2
  Low:      0
```

## Priority Legend

- 🔴 **● High** - Urgent and important tasks
- 🟡 **◐ Medium** - Standard priority (default)
- 🔵 **○ Low** - Can wait

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
├── task_manager.py             # Main application
├── test_task_manager.py        # Test suite
├── requirements.txt            # Python dependencies
├── tasks.json                  # Task storage (created on first run)
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
├── AGENTS.md                   # AI usage documentation
└── README.md                   # This file
```

## How It Works

Tasks are stored in a JSON file (`tasks.json`) that persists between sessions. Each task includes:
- Title
- Priority (low/medium/high)
- Due date (optional)
- Completion status
- Creation timestamp

The application automatically sorts tasks to show:
1. Incomplete tasks first (by priority: high → medium → low)
2. Completed tasks last

## AI-Assisted Development

This project was developed with assistance from AI tools including Claude. For details on how AI was used in the development process, see [AGENTS.md](AGENTS.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Enhancements

Potential features for future versions:
- Search tasks by keyword
- Task categories/tags
- Recurring tasks
- Export to CSV or other formats
- Undo last action
- Smart date parsing ("tomorrow", "next week")

## Contributing

This is an educational project for IS4010. Suggestions and feedback are welcome!

---

**Made with ❤️ and Python**