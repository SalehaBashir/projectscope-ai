from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.rag.documents import load_knowledge_base


def _build_document_text(document: dict) -> str:
    parts = [
        document.get("name", ""),
        document.get("description", ""),
        " ".join(document.get("keywords", [])),
        " ".join(document.get("requirements", [])),
        " ".join(document.get("features", [])),
        " ".join(document.get("integrations", [])),
        " ".join(document.get("risks", [])),
    ]

    return " ".join(parts)


def retrieve_relevant_documents(
    query: str,
    top_k: int = 3,
) -> list[dict]:

    documents = [
    document
    for document in load_knowledge_base()
    if document.get("approved", False) is True
]

    if not documents:
        return []

    document_texts = [
        _build_document_text(document)
        for document in documents
    ]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
    )

    document_vectors = vectorizer.fit_transform(document_texts)
    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(
        query_vector,
        document_vectors,
    )[0]

    ranked_indexes = similarities.argsort()[::-1]

    results = []

    for index in ranked_indexes[:top_k]:
        score = similarities[index]

        if score > 0:
            document = documents[index].copy()
            document["retrieval_score"] = round(float(score), 4)
            results.append(document)

    return results