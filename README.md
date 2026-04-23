# df-home-project

A CLI tool that chats with Claude AI and queries an SQLite employees database using natural language or raw SQL. Logs are formatted as `[INFO]: {message}`.

## Setup

**Install the package:**
```bash
pip install -e .
```

This installs all dependencies (including `anthropic`) and registers the `df-home` CLI command.

**Set your API key:**
```bash
# Linux/macOS
export ANTHROPIC_API_KEY="your-key-here"

# PowerShell
$env:ANTHROPIC_API_KEY = "your-key-here"
```

## Usage

Run the interactive CLI:
```bash
df-home
```

On startup, the app connects to `employees.db`, picks a random department as a guardrail, and enters an interactive prompt.

### Chat with Claude

Prefix your input with `ask_llm:`:
```
You: ask_llm: What is a relational database?
[INFO]: Claude: A relational database is...
```

### Query the Database

All other input is treated as a database query. The app auto-detects whether it's SQL or natural language.

#### Natural language → SQL (translated by Claude)
```
You: show me all employees with a salary above 50000
[INFO]: SQL: SELECT * FROM employee WHERE salary > 50000 AND department = 'Engineering'
[INFO]: name | salary | department
[INFO]: --------------------------------
[INFO]: Alice | 90000 | Engineering
```

#### Raw SQL (runs directly)
SQL keywords (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `DROP`, `ALTER`, `PRAGMA`) trigger direct execution:
```
You: SELECT name, salary FROM employee ORDER BY salary DESC
[INFO]: name | salary
[INFO]: ----------
[INFO]: Alice | 120000
```

## Project Structure

```
df-home-project/
  pyproject.toml      # package config and dependencies
  employees.db        # SQLite database
  df_home/
    __init__.py
    main.py           # CLI entrypoint
```
