from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

_MODEL = None


def _model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def retrieve_policy(query: str, policy_dir: str = "data/policies", top_k: int = 3):
    chunks = []
    for path in sorted(Path(policy_dir).glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        for chunk in [x.strip() for x in text.split("\n\n") if x.strip()]:
            chunks.append({"source": path.name, "text": chunk})
    if not chunks:
        return []
    model = _model()
    query_vec = model.encode([query], normalize_embeddings=True)[0]
    doc_vecs = model.encode([c["text"] for c in chunks], normalize_embeddings=True)
    scores = np.dot(doc_vecs, query_vec)
    order = np.argsort(scores)[::-1][:top_k]
    return [{**chunks[i], "score": float(scores[i])} for i in order]
