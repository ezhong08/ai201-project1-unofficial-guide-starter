from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)

# How many recent chat messages (user+assistant turns) to keep as conversational
# memory. Capping this keeps token cost bounded and stops stale context from
# dominating later turns.
MAX_HISTORY_MESSAGES = 6


def _recent(history):
    """Return the last MAX_HISTORY_MESSAGES messages as {role, content} dicts."""
    if not history:
        return []
    # Gradio's "messages" format is already a list of {"role", "content"} dicts.
    return [
        {"role": m["role"], "content": m["content"]}
        for m in history[-MAX_HISTORY_MESSAGES:]
        if m.get("content")
    ]


def rewrite_query(query, history=None):
    """
    Turn a follow-up question into a standalone search query using recent
    conversation history, so retrieval works even when the question is
    elliptical (e.g. "What about on North campus?" after asking about Café
    Jennie). With no history, the query is returned unchanged.

    This is a cheap, best-effort step: if the rewrite call fails for any
    reason, we fall back to the original query.
    """
    recent = _recent(history)
    if not recent:
        return query

    convo = "\n".join(f"{m['role']}: {m['content']}" for m in recent)
    prompt = (
        "You resolve elliptical follow-up questions into standalone search queries.\n\n"
        "Rewrite the follow-up ONLY IF it depends on the prior conversation to be "
        "understood — i.e. it uses pronouns or references ('it', 'there', 'that one', "
        "'what about...') or omits the subject. In that case, substitute in the "
        "specific context (eatery name, campus, topic) it refers to.\n\n"
        "If the follow-up is already a complete, self-contained question — even if it "
        "introduces a NEW topic unrelated to the prior turns — return it EXACTLY "
        "unchanged. Do NOT inject names, eateries, or topics from earlier turns into a "
        "question that did not mention them. When in doubt, return it unchanged.\n\n"
        "Output ONLY the query, nothing else.\n\n"
        "Examples:\n"
        "Conversation:\n"
        "user: Where on campus is Café Jennie located?\n"
        "assistant: Café Jennie is in Mann Library on the Ag Quad.\n"
        "Follow-up: What are its hours?\n"
        "Standalone query: What are Café Jennie's hours?\n\n"
        "Conversation:\n"
        "user: What is the Bear Choice meal plan?\n"
        "assistant: It's an unlimited dining plan...\n"
        "Follow-up: Does Cornell provide reusable utensils? If so, where?\n"
        "Standalone query: Does Cornell provide reusable utensils? If so, where?\n\n"
        f"Conversation:\n{convo}\n\n"
        f"Follow-up: {query}\n\n"
        "Standalone query:"
    )
    try:
        resp = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=80,
        )
        rewritten = (resp.choices[0].message.content or "").strip()
        return rewritten or query
    except Exception:
        return query


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved Cornell dining chunks.

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "article"  : the source/article name
      - "distance" : similarity score (you can use this to filter weak matches)

    `query` has already been rewritten into a standalone query by `rewrite_query`
    in app.py, so no conversational history is needed here — the question is
    always self-contained.

    Design points worth talking through with your group:
      - How will you format the chunks into a context block for the prompt?
      - What instructions will stop the model from answering beyond what the
        sources say? (Grounding is the whole point — a confident wrong answer
        is worse than an honest "I don't know.")
      - How will you surface which source each answer comes from?

    The response should:
      1. Answer using only the retrieved context — not the model's general knowledge
      2. Make clear which source the answer comes from
      3. Say so clearly when the answer isn't in the loaded dining sources

    Return the response as a plain string.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded Cornell dining sources. "
            "Try rephrasing your question — or check that your ingestion pipeline is working."
        )

    # Context formatting: a single numbered block, one entry per chunk, each
    # labeled with its source article. We keep "text" and "article" but drop
    # "distance" — that's an internal retrieval signal the model doesn't need.
    context = "\n".join(
        f"[{i}] ({chunk['article']}) {chunk['text']}"
        for i, chunk in enumerate(retrieved_chunks, start=1)
    )

    # Grounding instruction: pin the model to the provided excerpts as its
    # only source of truth so it can't fall back on general knowledge.

    system_prompt = (
        "You are the Cornell Dining Guide, an assistant that answers questions about "
        "Cornell University dining — eateries, meal plans, hours, payment options, and "
        "where to eat around campus and Ithaca.\n\n"
        "Answer ONLY using the excerpts provided in the context below. These excerpts "
        "are your single source of truth. Do not use any outside knowledge about Cornell "
        "dining, even if you are confident you know the answer — your own training "
        "knowledge is not allowed here.\n\n"
        "- If the context contains the answer, respond using only what it says.\n"
        "- If the context does NOT contain enough information to answer the question, "
        "do not guess or fill in gaps. Say clearly that the loaded dining sources don't cover it.\n"
        "- Never invent eateries, prices, hours, or details that are not in the context.\n"
        "- The sources include ranked lists (e.g. a numbered \"best colleges for food\" "
        "list, where #1 is best) and tier ratings (S/A/B/C, where S is highest). When a "
        "question asks you to compare items, you MAY use these rankings or tiers as "
        "evidence — an item with a better rank or higher tier is rated more highly by that "
        "source. Draw that comparison and cite the specific ranks/tiers you used; this is "
        "grounded reasoning, not outside knowledge.\n"
        "- Keep in mind the excerpts may reflect a specific point in time (e.g. hours or "
        "whether a place is open), so present those details as coming from the source rather "
        "than as guaranteed current facts.\n"
        "- State which source your answer comes from.\n\n"
        "A confident wrong answer is worse than honestly saying you don't know. "
        "At the end of every response, if the source was not mentioned yet, mention it in the form (source name)."
    )

    # Message structure: instructions go in the system message; recent prior
    # turns supply conversational memory; the retrieved context and the user's
    # current question go in the final user message.
    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    messages = [{"role": "system", "content": system_prompt}]
    # No conversational history is injected here — the query has already been
    # rewritten into a standalone question by rewrite_query(), so prior turns
    # would only add noise and potentially mislead the model.
    messages.append({"role": "user", "content": user_message})

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
    )

    return response.choices[0].message.content
