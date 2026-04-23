#!/usr/bin/env python3
import sys
import sqlite3
import anthropic

DB_PATH = "employees.db"


def ask_claude(user_input: str) -> None:
    client = anthropic.Anthropic()
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_input}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    print()


def get_schema() -> str:
    try:
        con = sqlite3.connect(DB_PATH)
        tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        schema_parts = []
        for (table,) in tables:
            info = con.execute(f"PRAGMA table_info({table})").fetchall()
            cols = ", ".join(f"{row[1]} {row[2]}" for row in info)
            schema_parts.append(f"{table}({cols})")
        con.close()
        return "\n".join(schema_parts) if schema_parts else "No tables found."
    except sqlite3.Error as e:
        return f"Could not read schema: {e}"


def natural_language_to_sql(user_input: str) -> str:
    schema = get_schema()
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        system=(
            "You are a SQL expert. Convert the user's natural language request into a single valid SQLite query. "
            "Respond with ONLY the raw SQL — no markdown, no explanation, no code fences."
        ),
        messages=[
            {"role": "user", "content": f"Database schema:\n{schema}\n\nRequest: {user_input}"},
        ],
    )
    return response.content[0].text.strip()


def query_db(sql: str) -> None:
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.execute(sql)
        rows = cur.fetchall()
        if cur.description:
            headers = [col[0] for col in cur.description]
            print(" | ".join(headers))
            print("-" * (sum(len(h) for h in headers) + 3 * (len(headers) - 1)))
            for row in rows:
                print(" | ".join(str(v) for v in row))
        else:
            con.commit()
            print(f"OK ({cur.rowcount} rows affected)")
        con.close()
    except sqlite3.Error as e:
        print(f"DB error: {e}")


SQL_KEYWORDS = {"select", "insert", "update", "delete", "create", "drop", "alter", "pragma"}


def handle_db_request(user_input: str) -> None:
    first_word = user_input.strip().split()[0].lower() if user_input.strip() else ""
    if first_word in SQL_KEYWORDS:
        query_db(user_input)
    else:
        sql = natural_language_to_sql(user_input)
        print(f"SQL: {sql}")
        query_db(sql)


def main():
    args = sys.argv[1:]

    if args and args[0] == "--db":
        user_input = " ".join(args[1:])
        if not user_input:
            print("Usage: main.py --db <natural language request>")
            sys.exit(1)
        handle_db_request(user_input)
    elif args:
        ask_claude(" ".join(args))
    else:
        try:
            while True:
                line = input("You: ").strip()
                if not line:
                    continue
                if line.lower().startswith("db:"):
                    handle_db_request(line[3:].strip())
                else:
                    ask_claude(line)
        except (EOFError, KeyboardInterrupt):
            pass


if __name__ == "__main__":
    main()
