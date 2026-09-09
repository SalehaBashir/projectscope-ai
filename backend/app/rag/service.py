from app.rag.retriever import retrieve_relevant_documents


def build_rag_context(
    project_description: str,
    top_k: int = 3,
) -> str:
    documents = retrieve_relevant_documents(
        project_description,
        top_k=top_k,
    )

    if not documents:
        return "No relevant domain knowledge was found."

    context_parts = []

    for document in documents:
        context_parts.append(
            f"""
Domain: {document.get("name", "")}

Description:
{document.get("description", "")}

Typical Requirements:
{chr(10).join("- " + item for item in document.get("requirements", []))}

Typical Features:
{chr(10).join("- " + item for item in document.get("features", []))}

Common Integrations:
{chr(10).join("- " + item for item in document.get("integrations", []))}

Common Risks:
{chr(10).join("- " + item for item in document.get("risks", []))}
""".strip()
        )

    return "\n\n---\n\n".join(context_parts)