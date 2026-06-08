"""
eval_hybrid.py — Compare hybrid search (semantic + BM25) vs. semantic-only retrieval.

Runs the same evaluation queries through both retrieve() and hybrid_retrieve()
and prints side-by-side results so we can judge whether the hybrid approach
improves relevance.

Usage:
  python eval_hybrid.py
"""

import sys

from ingest import load_documents, chunk_document
from retriever import embed_and_store, retrieve, hybrid_retrieve, get_collection, _rebuild_bm25_index

# Evaluation queries from planning.md (3 of 5)
QUERIES = [
    "What is the cost of the Bear Choice meal plan for undergraduates over 1 semester?",
    "What is the Spotted Duck sweet place known for?",
    "Which general region of the Cornell campus is Café Jennie located?",
    "Is Cornell considered to have better food than Rice University?",
    "Does Cornell provide reusable utensils? If so, where?",
]

# Test with different alpha values to show the spectrum
ALPHA_VALUES = [1.0, 0.5, 0.0]
# alpha=1.0 = pure semantic, alpha=0.5 = balanced hybrid, alpha=0.0 = pure BM25


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
    _rebuild_bm25_index()
    print()


def print_separator(char="=", width=80):
    print(char * width)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ensure_index()

    # Build BM25 index if needed
    _rebuild_bm25_index()

    print_separator()
    print("  HYBRID SEARCH vs. SEMANTIC-ONLY COMPARISON")
    print_separator()

    for q_idx, query in enumerate(QUERIES, start=1):
        print_separator("-")
        print(f"Query #{q_idx}: {query}")
        print_separator("-")

        # Run all retrieval methods
        sem_results = retrieve(query)

        for alpha in ALPHA_VALUES:
            label = {
                1.0: "Semantic-only (α=1.0)",
                0.5: "Hybrid balanced (α=0.5)",
                0.0: "BM25-only (α=0.0)",
            }[alpha]

            if alpha == 1.0:
                # Already ran retrieve() above, reuse results
                results = sem_results
            else:
                results = hybrid_retrieve(query, alpha=alpha)

            print(f"\n  [{label}]")
            if not results:
                print("    (no results)")
                continue
            for rank, chunk in enumerate(results, start=1):
                dist = chunk.get("distance", 0)
                bm25 = chunk.get("bm25_score", 0)
                hybrid = chunk.get("hybrid_score", 0)
                if alpha == 1.0:
                    extra = f"dist={dist:.3f}"
                elif alpha == 0.0:
                    extra = f"bm25={bm25:.3f}"
                else:
                    extra = f"hybrid={hybrid:.3f}  sem_dist={dist:.3f}  bm25={bm25:.3f}"
                print(f"    [{rank}] {extra}  [{chunk['article']}]")
                print(f"           {chunk['text'][:120]}...")
        print()

    print_separator()
    print("  SUMMARY: Compare the top results above.")
    print("  - Semantic (α=1.0): best for conceptual/meaning-based queries")
    print("  - BM25 (α=0.0):     best for exact keyword/entity matching")
    print("  - Hybrid (α=0.5):   balances both approaches via RRF")
    print_separator()


if __name__ == "__main__":
    main()