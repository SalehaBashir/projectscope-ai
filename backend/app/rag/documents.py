import json
from pathlib import Path


KNOWLEDGE_FILE = Path(__file__).parent / "knowledge" / "project_patterns.json"


def load_knowledge_base() -> list[dict]:
    if not KNOWLEDGE_FILE.exists():
        raise FileNotFoundError(
            f"RAG knowledge base not found: {KNOWLEDGE_FILE}"
        )

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("RAG knowledge base must contain a JSON list.")

    return data