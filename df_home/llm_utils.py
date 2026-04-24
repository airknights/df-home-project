import logging
import anthropic

log = logging.getLogger(__name__)


def ask_llm(user_input: str) -> None:
    client = anthropic.Anthropic()
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_input}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    print()


def natural_language_to_sql(user_input: str, selected_department: str, schema: str) -> str:
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
