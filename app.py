import gradio as gr
from ingest import load_documents, chunk_document
from retriever import embed_and_store, retrieve, hybrid_retrieve, get_collection
from generator import generate_response, rewrite_query


# ---------------------------------------------------------------------------
# Ingestion — runs once on startup
# ---------------------------------------------------------------------------

def run_ingestion():
    """
    Load rule documents, chunk them, and store in ChromaDB.

    If the vector store is already populated, ingestion is skipped.
    To re-ingest (e.g. after changing your chunking strategy), delete the
    ./chroma_db folder and restart the app.
    """
    collection = get_collection()

    if collection.count() > 0:
        print(f"Vector store already populated ({collection.count()} chunks). Skipping ingestion.")
        print("To re-ingest, delete the ./chroma_db folder and restart.")
        return

    print("Ingesting Cornell dining documents...")
    documents = load_documents()
    all_chunks = []

    for doc in documents:
        chunks = chunk_document(doc["text"], doc["article"])
        all_chunks.extend(chunks)

    if all_chunks:
        embed_and_store(all_chunks)
        print(f"Ingestion complete. {len(all_chunks)} chunks stored.")
    else:
        print(
            "\n⚠️  No chunks produced. Make sure chunk_document() is implemented in ingest.py.\n"
            "    Cornell dining will start, but won't be able to answer questions yet.\n"
        )


# ---------------------------------------------------------------------------
# Chat handler
# ---------------------------------------------------------------------------

def chat(message, history):
    if not message.strip():
        return ""
    # Conversational memory: rewrite an elliptical follow-up into a standalone
    # query (using prior turns) so retrieval still finds the right chunks.
    # The rewritten query is passed directly to generation so the LLM never
    # sees a potentially ambiguous elliptical question or gets confused by
    # prior conversation history.
    search_query = rewrite_query(message, history)
    # retrieved = retrieve(search_query)
    retrieved = hybrid_retrieve(search_query, alpha=0.5)
    return generate_response(search_query, retrieved)


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

with gr.Blocks(
    title="Cornell dining",
) as demo:

    gr.HTML("""
        <div style="text-align:center; padding:1.25rem 0 0.5rem;">
            <h1 style="font-size:2rem; font-weight:700; color:#312e81; margin:0;">
                🍽️ Cornell Dining Guide
            </h1>
            <p style="color:#6b7280; font-size:1rem; margin:0.4rem 0 0;">
                Ask anything about Cornell eateries, meal plans, and where to eat around Ithaca —
                answers grounded in real dining guides and student reviews.
            </p>
        </div>
    """)

    with gr.Row():
        with gr.Column(scale=3):
            gr.ChatInterface(
                fn=chat,
                chatbot=gr.Chatbot(
                    height=440,
                    placeholder=(
                        "<div style='text-align:center; color:#9ca3af; margin-top:3rem;'>"
                        "Ask a question about Cornell dining to get started 🍴"
                        "</div>"
                    ),
                ),
                textbox=gr.Textbox(
                    placeholder='e.g. "Where on campus is Café Jennie located?"',
                    container=False,
                    scale=7,
                ),
                examples=[
                    "What is the cost of the Bear Choice meal plan for one semester?",
                    "Where on campus is Café Jennie located?",
                    "What is the Spotted Duck known for?",
                    "Where can I get bagels on central campus?",
                    "What payment methods does Cornell Dining accept?",
                    "What's a good restaurant in Collegetown?",
                    "Does Cornell have good food compared to other colleges?",
                    "Where can I get ice cream on campus?",
                    "What are the best restaurants in Ithaca for students?",
                ],
                cache_examples=False,
            )

        with gr.Column(scale=1, min_width=180):
            gr.HTML("""
                <div style="background:#f5f3ff; border:1px solid #ddd6fe;
                            border-radius:10px; padding:1rem; margin-top:0.5rem;">
                    <p style="font-size:0.8rem; font-weight:700; color:#4c1d95;
                               margin:0 0 0.5rem; letter-spacing:0.05em;">
                        📚 WHAT I KNOW ABOUT
                    </p>
                    <ul style="font-size:0.85rem; color:#5b21b6; list-style:none;
                                padding:0; margin:0; line-height:1.8;">
                        <li>🍽️ Campus eateries (Central, North, West)</li>
                        <li>💳 Meal plans & rates</li>
                        <li>📖 Guide to Cornell Dining</li>
                        <li>🎥 Student dining rankings</li>
                        <li>🍰 Sweets & ice cream spots</li>
                        <li>🌆 Collegetown & Ithaca restaurants</li>
                        <li>🏫 College food comparisons</li>
                    </ul>
                    <hr style="border:none; border-top:1px solid #ddd6fe; margin:0.75rem 0;">
                    <p style="font-size:0.75rem; color:#7c3aed; margin:0; line-height:1.5;">
                        Answers are grounded in the loaded dining sources only. If
                        something isn't covered, the guide will say so.
                    </p>
                </div>
            """)


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  Cornell dining — starting up")
    print("="*50 + "\n")
    run_ingestion()
    demo.launch(theme=gr.themes.Soft(primary_hue="indigo"))