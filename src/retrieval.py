# src/retrieval.py
import re
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.data_loader import KBDoc


@dataclass
class KBChunk:
    doc_filename: str
    doc_category: str
    section_title: str
    content: str


def chunk_kb_docs(kb_docs: list[KBDoc]) -> list[KBChunk]:
    """Split each KB doc into sections at H1/H2 headings, so files covering
    multiple topics (like performance-and-integrations.md) don't get treated
    as one giant blob during retrieval."""
    chunks = []
    for doc in kb_docs:
        parts = re.split(r'\n(?=#{1,2} )', doc.content)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            title_line = part.splitlines()[0].lstrip("#").strip()
            chunks.append(KBChunk(
                doc_filename=doc.filename,
                doc_category=doc.category,
                section_title=title_line,
                content=part,
            ))
    return chunks


class KBRetriever:
    def __init__(self, chunks: list[KBChunk]):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform([c.content for c in chunks])

    def search(self, query: str, top_k: int = 3) -> list[tuple[KBChunk, float]]:
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        ranked = sorted(zip(self.chunks, scores), key=lambda x: -x[1])
        return [r for r in ranked[:top_k] if r[1] > 0]


if __name__ == "__main__":
    from src.data_loader import load_kb_docs, load_tickets

    docs = load_kb_docs()
    chunks = chunk_kb_docs(docs)
    print(f"Chunked {len(docs)} docs into {len(chunks)} sections\n")

    retriever = KBRetriever(chunks)

    # test with a synthetic query
    test_query = "dashboard is loading really slowly and timing out"
    print(f"Query: {test_query!r}")
    for chunk, score in retriever.search(test_query):
        print(f"  {score:.3f}  {chunk.doc_filename} -> {chunk.section_title}")

    # test with a REAL ticket from your data
    print()
    tickets = load_tickets()
    real_ticket = tickets[0]
    query2 = f"{real_ticket.subject}\n{real_ticket.body}"
    print(f"Real ticket: {real_ticket.ticket_id} - {real_ticket.subject!r}")
    for chunk, score in retriever.search(query2):
        print(f"  {score:.3f}  {chunk.doc_filename} -> {chunk.section_title}")