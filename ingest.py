import os
from config import DOCS_PATH


def load_documents():
    """Load all .txt documents from the docs folder."""
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            article_name = filename.replace(".txt", "").replace("_", " ").title()
            documents.append({
                "article": article_name,
                "filename": filename,
                "text": text,
            })
    print(f"Loaded {len(documents)} document(s): {[d['article'] for d in documents]}")
    return documents


def chunk_document(text, article_name):
    """
    Split a document into chunks ready for embedding.

    This function is already implemented — read through it and the inline
    comments before moving on. The decisions made here directly shape what
    retrieval returns in Milestones 2 and 3, so it's worth understanding
    before you build on top of it.

    Strategy: character-based sliding window with overlap.
      - chunk_size = 300 characters: long enough to carry the semantic
        meaning of a single answer, short enough to return targeted results
      - overlap = 50 characters: duplicates a small window of text at each
        boundary so a answer that spans two chunks can still be retrieved intact
      - min_length = 50 characters: filters out whitespace artifacts and
        very short fragments that add noise without useful semantic content

    Returns a list of dicts, each with:
      - "text"     : the chunk text (str)
      - "article"  : the article name,
      - "chunk_id" : a unique identifier
    """
    chunk_size = 300
    overlap = 50
    min_length = 50

    chunks = []
    prefix = article_name.lower().replace(" ", "_")
    counter = 0

    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()

        if len(chunk_text) >= min_length:
            chunks.append({
                "text": chunk_text,
                "article": article_name,
                "chunk_id": f"{prefix}_{counter}",
            })
            counter += 1

        # Advance by (chunk_size - overlap) so the next chunk shares
        # `overlap` characters with the tail of this one.
        start += chunk_size - overlap

    return chunks
