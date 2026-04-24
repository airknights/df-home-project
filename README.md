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

## Architecture decisions

Almost all default pathways is as follows

1. startup 
2. department randomly selected and logged 
3. input sent to llm 
4. query generated with guardrails 
5. query ran 
6. results returned

Optional pathway includes prefix with ask_llm: where ended questions to llm is possible.  This is mostly for debug testing.

1. startup 
2. department randomly selected and logged 
3. input sent to llm 
4. answer from llm printed

Optional Direct query pathway: this is to determine the data sets and any time I want to query db for whatever reason.
1. startup 
2. department randomly selected and logged  
5. query ran 
6. results returned


## Notice on AI usage

I did use claude code to generate the general structure and scaffolding code.  I didn't want to waste time with 
scaffolding it manually mainly because it would require me to look up multiple document sources and spend almost
3X the amount of time to generate ultimately the same code.

I did also ask it to do some autocomplete stuff (built into pycharm via AI).


## Weaknesses

It's not capable of handling all kinds of natural language.  Which will need additional training and/or guadrails or detailed queries.

example: Marketing department, I wanted to get the brand managers, so I asked:

"show me all the brand folks"

For which the query generated is 
```sql
 SELECT * FROM Employee WHERE Department = 'Marketing'
```

However, when I said: "give me everyone with a brand in the title"

it generated:
SELECT * FROM Employee WHERE Department = 'Marketing' AND Role LIKE '%Brand%'


