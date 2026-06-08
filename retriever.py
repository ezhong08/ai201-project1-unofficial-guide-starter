import chromadb
from rank_bm25 import BM25Okapi
from chromadb.utils import embedding_functions
from config import CHROMA_COLLECTION, CHROMA_PATH, EMBEDDING_MODEL, N_RESULTS

# Embedding function and ChromaDB client are initialized once at module load.
# sentence-transformers downloads the model on first use — this may take
# 30–60 seconds the very first time. Subsequent runs use a local cache.
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    """Return the ChromaDB collection. Used by app.py during ingestion."""
    return _collection


def embed_and_store(chunks):
    """
    Embed a list of chunks and store them in the vector database.

    This function is already implemented — read through it before moving on.

    _collection.add() takes three parallel lists built from the chunks
    returned by chunk_document():
      - documents : raw text strings — ChromaDB's embedding function converts
                    these to vectors automatically using sentence-transformers
      - metadatas : one dict per chunk, stored alongside the vector so that
                    retrieve() can surface which article a result came from
      - ids       : the unique chunk_id strings used to identify each entry

    You don't generate embeddings manually here — you hand over the text
    and ChromaDB handles the vector math.
    """
    _collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"article": c["article"]} for c in chunks],
        ids=[c["chunk_id"] for c in chunks],
    )
    print(f"Stored {_collection.count()} total chunks in the vector database.")


# ---------------------------------------------------------------------------
# BM25 index (lazily built from all stored documents)
# ---------------------------------------------------------------------------

_bm25_index = None
_bm25_chunk_ids = None


def _rebuild_bm25_index():
    """
    Build a BM25 index over every chunk stored in the ChromaDB collection.

    The index is cached globally so it only rebuilds when new chunks are added.
    """
    global _bm25_index, _bm25_chunk_ids

    count = _collection.count()
    if count == 0:
        _bm25_index = None
        _bm25_chunk_ids = []
        return

    # Fetch all stored chunks
    all_data = _collection.get(include=["documents", "metadatas"])
    documents = all_data["documents"]
    metadatas = all_data["metadatas"]
    ids = all_data["ids"]

    if not documents:
        _bm25_index = None
        _bm25_chunk_ids = []
        return

    # Tokenize each document into a list of lowercase tokens for BM25
    tokenized_corpus = [doc.lower().split() for doc in documents]

    _bm25_index = BM25Okapi(tokenized_corpus)
    _bm25_chunk_ids = ids
    print(f"Rebuilt BM25 index over {len(documents)} chunks.")


def _get_bm25_scores(query, n_results=N_RESULTS):
    """
    Run BM25 keyword search and return scored chunks in the same format
    as the semantic retrieve() function.

    Returns a list of dicts with keys: text, article, distance, bm25_score.
    The 'distance' is a pseudo-distance (1 / (1 + bm25_score)) so that
    lower = more relevant, matching the semantic convention.
    """
    global _bm25_index
    if _bm25_index is None:
        _rebuild_bm25_index()
    if _bm25_index is None:
        return []

    tokenized_query = query.lower().split()
    bm25_scores = _bm25_index.get_scores(tokenized_query)

    # Get all documents to return text/article for the top BM25 results
    all_data = _collection.get(include=["documents", "metadatas"])
    documents = all_data["documents"]
    metadatas = all_data["metadatas"]
    ids = all_data["ids"]

    # Create list of (score, idx) pairs and sort descending by BM25 score
    scored = [(bm25_scores[i], i) for i in range(len(bm25_scores))]
    scored.sort(key=lambda x: x[0], reverse=True)

    # Take top n_results
    top_n = scored[:n_results]

    results = []
    for bm25_score, idx in top_n:
        if bm25_score <= 0:
            continue
        # Convert BM25 score to pseudo-distance so lower = more relevant
        pseudo_distance = 1.0 / (1.0 + bm25_score)
        results.append({
            "text": documents[idx],
            "article": metadatas[idx]["article"],
            "distance": pseudo_distance,
            "bm25_score": bm25_score,
        })
    return results


# ---------------------------------------------------------------------------
# Retrieval methods
# ---------------------------------------------------------------------------


def retrieve(query, n_results=N_RESULTS):
    """
    Find the most relevant rule chunks for a user's question.

    Uses ChromaDB semantic search (cosine similarity on sentence-transformer
    embeddings). Returns a list of dicts, each with:
      - "text"     : the chunk text
      - "article"  : the article name (pull this from metadatas)
      - "distance" : the similarity score (lower = more similar for cosine)

    Note: _collection.query() returns nested lists (one per query). You only
    have one query, so you'll want index [0] to get the actual results.
    """
    if _collection.count() == 0:
        return []

    results = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    # query() nests one list per query in query_texts; we passed one query,
    # so index [0] unwraps it into this query's parallel result lists.
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    chunks = [
        {"text": text, "article": meta["article"], "distance": distance}
        for text, meta, distance in zip(documents, metadatas, distances)
    ]

    for chunk in chunks:
        print(f"[{chunk['article']}] (dist: {chunk['distance']:.3f}) {chunk['text'][:80]}...")

    return chunks


def hybrid_retrieve(query, n_results=N_RESULTS, alpha=0.5):
    """
    Hybrid search combining semantic (cosine) and keyword (BM25) retrieval.

    Uses Reciprocal Rank Fusion (RRF) to merge results from both approaches.
    
    Parameters:
      query     : the user's question string
      n_results : number of final results to return
      alpha     : weight for semantic search (0 = pure BM25, 1 = pure semantic)

    Returns a list of dicts, each with:
      - "text"        : the chunk text
      - "article"     : the article name
      - "distance"    : semantic distance (cosine)
      - "bm25_score"  : raw BM25 score (0 if not in BM25 top-k)
      - "hybrid_score": combined RRF score (higher = more relevant)
    """
    if _collection.count() == 0:
        return []

    # 1) Get semantic results
    semantic_results = _collection.query(
        query_texts=[query],
        n_results=n_results * 3,  # fetch more for better fusion
        include=["documents", "metadatas", "distances"],
    )

    sem_docs = semantic_results["documents"][0]
    sem_metas = semantic_results["metadatas"][0]
    sem_dists = semantic_results["distances"][0]

    # 2) Get BM25 results (with more candidates for fusion)
    tokenized_query = query.lower().split()
    bm25_results = _get_bm25_scores(query, n_results=n_results * 3)

    # 3) Reciprocal Rank Fusion
    #    RRF score = sum over rankers of 1 / (k + rank_of_doc_in_ranker)
    k = 60  # RRF constant

    # Build a map of chunk text -> fused score info
    fused = {}

    # Add semantic results
    for i, (doc, meta, dist) in enumerate(zip(sem_docs, sem_metas, sem_dists)):
        rank = i + 1  # 1-based rank
        rrf_score = 1.0 / (k + rank)
        fused[doc] = {
            "text": doc,
            "article": meta["article"],
            "distance": dist,
            "bm25_score": 0.0,
            "hybrid_score": alpha * rrf_score,
        }

    # Add BM25 results and fuse
    for i, bm25_chunk in enumerate(bm25_results):
        rank = i + 1
        rrf_score = 1.0 / (k + rank)
        text = bm25_chunk["text"]
        if text in fused:
            fused[text]["bm25_score"] = bm25_chunk["bm25_score"]
            fused[text]["hybrid_score"] += (1 - alpha) * rrf_score
        else:
            fused[text] = {
                "text": text,
                "article": bm25_chunk["article"],
                "distance": bm25_chunk["distance"],
                "bm25_score": bm25_chunk["bm25_score"],
                "hybrid_score": (1 - alpha) * rrf_score,
            }

    # Sort by hybrid score descending (higher = more relevant)
    sorted_chunks = sorted(fused.values(), key=lambda x: x["hybrid_score"], reverse=True)

    # Take top n_results
    final_results = sorted_chunks[:n_results]

    print(f"\n--- Hybrid results (α={alpha}) ---")
    for chunk in final_results:
        print(
            f"  [{chunk['article']}] "
            f"hybrid={chunk['hybrid_score']:.3f} "
            f"sem_dist={chunk['distance']:.3f} "
            f"bm25={chunk['bm25_score']:.3f}  "
            f"{chunk['text'][:80]}..."
        )

    return final_results