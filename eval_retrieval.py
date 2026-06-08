"""
eval_retrieval.py — Milestone 4 retrieval sanity check.

Rebuilds the vector store if needed, then runs a few of the Evaluation Plan
queries through retrieve() and prints the returned chunks with their distance
scores so we can judge by hand whether retrieval is surfacing relevant text.

Usage:
  python eval_retrieval.py
"""

import sys

from ingest import load_documents, chunk_document
from retriever import embed_and_store, retrieve, get_collection

# Three of the five Evaluation Plan questions (from planning.md).
QUERIES = [
    "What is the cost of the Bear Choice meal plan for undergraduates over 1 semester?",
    "What is the Spotted Duck sweet place known for?",
    "Which general region of the Cornell campus is Café Jennie located?",
]


def ensure_index():
    """Populate the vector store from documents/ if it's empty."""
    collection = get_collection()
    if collection.count() > 0:
        print(f"Vector store already populated ({collection.count()} chunks).\n")
        return

    print("Building vector store from documents/ ...")
    all_chunks = []
    for doc in load_documents():
        all_chunks.extend(chunk_document(doc["text"], doc["article"]))
    embed_and_store(all_chunks)
    print()


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ensure_index()

    for q in QUERIES:
        print("=" * 80)
        print(f"QUERY: {q}")
        print("=" * 80)
        results = retrieve(q)
        if not results:
            print("  (no results)\n")
            continue
        for rank, chunk in enumerate(results, start=1):
            print(f"\n[{rank}] distance={chunk['distance']:.3f}  source={chunk['article']}")
            print(f"    {chunk['text']}")
        print()


if __name__ == "__main__":
    main()
