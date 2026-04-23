# df-home-project CLI

A CLI tool that chats with Claude AI and queries an SQLite employees database using natural language.

## Setup

**Install dependencies:**
```bash
pip install anthropic
```

**Set your API key:**
```bash
# Linux/macOS
export ANTHROPIC_API_KEY="your-key-here"

# PowerShell
$env:ANTHROPIC_API_KEY = "your-key-here"
```

## Usage

### Chat with Claude

Pass a question as an argument:
```bash
python main.py "What is the capital of France?"
```

Or run interactively:
```bash
python main.py
You: Explain what a binary tree is
You: What are some sorting algorithms?
```

### Query the Database

The database file is `employees.db` in the project directory.

#### Natural language (translated to SQL by Claude)
```bash
# Via flag
python main.py --db "show me all employees with a salary above 50000"
python main.py --db "who are the top 5 highest paid employees"
python main.py --db "how many employees are in each department"

# Interactive — prefix with "db:"
You: db: show me all employees
You: db: who earns the most
```

#### Raw SQL (runs directly)
```bash
# Via flag
python main.py --db "SELECT * FROM employees"
python main.py --db "INSERT INTO employees (name, role, salary) VALUES ('Alice', 'Engineer', 90000)"

# Interactive
You: db: SELECT name, salary FROM employees ORDER BY salary DESC
You: db: CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, role TEXT, salary REAL)
```

The `db:` interface auto-detects whether input is SQL or natural language — SQL keywords (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `DROP`, `ALTER`, `PRAGMA`) trigger direct execution; everything else is translated by Claude first.

When natural language is used, the generated SQL is printed before results:
```
SQL: SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 5
name  | salary
------------
Alice | 120000
...
```
