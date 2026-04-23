#!/usr/bin/env python3
import logging
import random
import sys
import sqlite3
import anthropic

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(levelname)s]: %(message)s")

log = logging.getLogger(__name__)

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


def natural_language_to_sql(user_input: str, selected_department) -> str:
    schema = get_schema()
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        system=(
            "You are a SQL expert. Convert the user's natural language request into a single valid SQLite query. "
            f"queries must include selected department to be {selected_department}"
            "Respond with ONLY the raw SQL — no markdown, no explanation, no code fences."
        ),
        messages=[
            {"role": "user", "content": f"Database schema:\n{schema}\n\nRequest: {user_input}"},
        ],
    )
    return response.content[0].text.strip()


def query_db(sql: str, **kwargs) -> None:
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.execute(sql)
        rows = cur.fetchall()
        if kwargs.get("return_data"):
            return rows

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
        log.error("DB error: %s", e)


SQL_KEYWORDS = {"select", "insert", "update", "delete", "create", "drop", "alter", "pragma"}


def handle_db_request(user_input: str, selected_department: str) -> None:
    first_word = user_input.strip().split()[0].lower() if user_input.strip() else ""
    if first_word in SQL_KEYWORDS:
        query_db(user_input, selected_department=selected_department)
    else:
        sql = natural_language_to_sql(user_input, selected_department=selected_department)
        log.info("SQL: %s", sql)
        query_db(sql)


def main():
    try:
        # guardrail: query db to get department and then set one at random
        data_rows = query_db("select distinct department from employee", return_data=True)
        data_rows_num_items = len(data_rows)
        if data_rows_num_items > 0:
            random_dept_index = random.randrange(1, data_rows_num_items)
        else:
            exit("No departments found. Exiting")

        department_selected = data_rows[random_dept_index][0]

        log.info(f"Selected department: {department_selected}")

        while True:
            line = input("You: ").strip()
            if not line:
                continue
            if line.lower().startswith("ask_llm:"):
                ask_claude(line)
            else:
                handle_db_request(line[3:].strip(), selected_department=department_selected)
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
