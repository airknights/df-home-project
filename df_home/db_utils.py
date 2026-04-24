import logging
import sqlite3

log = logging.getLogger(__name__)

DB_PATH = "employees.db"

SQL_KEYWORDS = {"select", "insert", "update", "delete", "create", "drop", "alter", "pragma"}


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


def query_db(sql: str, **kwargs):
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


def handle_db_request(user_input: str, selected_department: str) -> None:
    from df_home.llm_utils import natural_language_to_sql

    first_word = user_input.strip().split()[0].lower() if user_input.strip() else ""
    if first_word in SQL_KEYWORDS:
        query_db(user_input)
    else:
        sql = natural_language_to_sql(user_input, selected_department=selected_department, schema=get_schema())
        log.info("SQL: %s", sql)
        query_db(sql)
