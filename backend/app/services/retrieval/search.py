import math
import re
from typing import List, Dict, Any

def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text to lowercase words."""
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return [w for w in cleaned.split() if len(w) > 2]

class KeywordRetriever:
    """
    In-memory BM25-style retriever for document chunks.
    Allows precision retrieval over uploaded documents without requiring
    heavy external vector database dependencies in Phase 2.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def rank_chunks(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 8) -> List[Dict[str, Any]]:
        if not chunks or not query.strip():
            return chunks[:top_k]

        query_tokens = tokenize(query)
        if not query_tokens:
            return chunks[:top_k]

        doc_count = len(chunks)
        avg_dl = sum(len(tokenize(c.get("text_content", ""))) for c in chunks) / max(1, doc_count)

        # Calculate document frequency (DF) for each query term
        df: Dict[str, int] = {}
        for token in query_tokens:
            df[token] = sum(1 for c in chunks if token in c.get("text_content", "").lower())

        scored_chunks = []
        for c in chunks:
            text = c.get("text_content", "")
            title = c.get("section_title", "") or ""
            c_tokens = tokenize(text)
            doc_len = len(c_tokens)

            score = 0.0
            for term in query_tokens:
                term_df = df.get(term, 0)
                if term_df == 0:
                    continue

                # IDF calculation with smoothing
                idf = math.log(1 + (doc_count - term_df + 0.5) / (term_df + 0.5))

                # Term frequency in chunk
                tf = c_tokens.count(term)
                # Boost if term occurs in section title
                if term in title.lower():
                    tf += 3

                # BM25 formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / max(1, avg_dl)))
                score += idf * (numerator / max(0.001, denominator))

            if score > 0:
                scored_chunks.append({**c, "_relevance_score": round(score, 4)})

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x.get("_relevance_score", 0), reverse=True)

        if not scored_chunks:
            # Fallback to returning initial chunks if no direct term match
            return chunks[:top_k]

        return scored_chunks[:top_k]

