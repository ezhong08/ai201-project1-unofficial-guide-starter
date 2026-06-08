# The Unofficial Guide â€” Project 1

> **How to use this template:**
> Complete each section _after_ you've built and tested the corresponding part of your system.
> Do not write placeholder text â€” if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] â€” useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

I chose dining at Cornell University as my domain. This knowledge is valuable to those dining at Cornell, especially newly admitted students who are unfamiliar with the situation. This knowledge in some cases can be found on Cornell's official websites, but this isn't always the case: For instance, YouTube videos about rankings of dining places would normally require a user to watch through parts of the video to get the information and explanations they need, which can be time consuming as it requires finding the video and clicking around to the right moment in the video.

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety â€” sources that together cover different subtopics or perspectives. -->

| #   | Source           | Description                                                    | URL or location                                                                           |
| --- | ---------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1   | Blog             | Overview of food rankings across colleges and universities.    | https://www.collegetransitions.com/blog/best-college-food/                                |
| 2   | Official Website | Dining options in central Cornell campus.                      | pdf/Central - Cornell Dining Now.pdf                                                      |
| 3   | YouTube Video    | Ranking of all Cornell restaurant options.                     | https://www.youtube.com/watch?v=oXL7lPaCTFQ                                               |
| 4   | YouTube Video    | Ranking of all places in Cornell for sweets.                   | https://www.youtube.com/watch?v=hR9lBcRT1pc                                               |
| 5   | YouTube Video    | Ranking of many places in the Finger Lakes region for food.    | https://www.youtube.com/watch?v=5qamJiAfKQI                                               |
| 6   | Official Website | A general guide to dining and dining options at Cornell.       | https://scl.cornell.edu/residential-life/dining/about-dining/guide-cornell-dining         |
| 7   | YouTube Video    | Ranking of many Ithaca dining options.                         | https://www.youtube.com/watch?v=v47vqblonJo                                               |
| 8   | Official Website | Dining options in north Cornell campus.                        | pdf/North - Cornell Dining Now.pdf                                                        |
| 9   | Official Website | Various meal plans for undergraduate students; includes costs. | https://scl.cornell.edu/residential-life/dining/meal-plans-rates/undergraduate-meal-plans |
| 10  | Official Website | Dining options in west Cornell campus.                         | pdf/West - Cornell Dining Now.pdf                                                         |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 300

**Overlap:** 50

**Why these choices fit your documents:** Although the text files are of different formats, they all consist of a certain place and then a few sentences describing that place, so a constant chunk size should be able to successfully capture each place.
I'd know my chunks were too small if retrieval returned a fragment with a rating but no restaurant name (or a name with no verdict) â€” answers would be unanswerable or attached to the wrong place. I'd know they were too large if a single chunk spanned several restaurants, because the embedding would blur multiple places together and a query about one eatery would pull in unrelated neighbors, diluting precision. 300/50 is my starting point; if my five evaluation questions show name/verdict splits, I'd raise the overlap before changing chunk size.

**Final chunk count:** 352

**Preprocessing before chunking:** YouTube transcripts joined into clean paragraphs; web pages extracted to text with `BeautifulSoup` (nav/header/footer stripped); PDFs extracted with `pdfplumber` with the "Cornell Dining Now" site nav/footer and icon-font glyphs removed, and each eatery's name line tagged with its campus (e.g. `(Central Campus)`) so the region rides into the embedding. Each document also keeps a `Name / Source` header so attribution survives into the chunks.

**Sample chunks:** (each ~300 characters with 50-character overlap, so consecutive chunks share a small window â€” visible in how several start mid-word/mid-sentence)

1. Source: **Central - Cornell Dining Now** (`central_-_cornell_dining_now_4`) â€” PDF eatery, with the campus tag added in preprocessing:

```
nature Sandwiches
Bus Stop Bagels Closed (Central Campus)
Kennedy Hall
Bagels for breakfast, bagels for lunch, bagels to go!
Featuring: Pepsi Beverages â€¢ Breakfast Sandwiches â€¢ Bagel Sandwiches â€¢ Snack Foods â€¢ 96oz Coffee2Go â€¢ Bigelow Tea â€¢
La Colombe Coffee
CafÃ© Jennie 10:00am â€“ 3:00pm (Central Cam
```

2. Source: **North - Cornell Dining Now** (`north_-_cornell_dining_now_7`) â€” PDF eatery on a different campus:

```
, specialty sandwiches, premium pastries, and drip coffee.
Featuring: Coffee (Hot) â€¢ Baked Goods â€¢ Breakfast Sandwiches â€¢ Panini and Signature Sandwiches â€¢ Peet's Coffee
Risley Dining Room Closed (North Campus)
Risley Residential College
Risley is our gluten-free, tree nut free and peanut free dinin
```

3. Source: **Undergraduate-Meal-Plans** (`undergraduate-meal-plans_5`) â€” meal-plan prices:

```
ergraduates
Bear Traditional
- $3,400 per semester; $6,800 per year
Up to 14 meals per week during designated service periods in the ten residential dining rooms
$400 Big Red Bucks per semester
4 bonus meals for guests per semester
Bear Choice
- $2,964 per semester; $5,928 per year
Up to 10 meals pe
```

4. Source: **Guide-Cornell-Dining** (`guide-cornell-dining_3`) â€” explanation of meal swipes / Big Red Bucks:

```
r on Friday, May 22, 2026. The meal plan program does not cover Cornellâ€™s recess for winter intersession. Big Red Bucks (BRBs) can be used during these recess periods.
What are meal swipes? What are BRBs?
Cornell Dining's
Traditional Meal Plans and West Campus House Meal Plans
all include both meal
```

5. Source: **Ranking 18 Sweet Pleasures At Cornell University** (`ranking_18_sweet_pleasures_at_cornell_university_14`) â€” YouTube review with a tier verdict:

```
ular soft serve place. It's 20 minutes out. I would say it's a... I would give it an A tier if it was nearer, but it's 20 minutes away. Oh, Spotted Duck. Ahh, Spotted Duck I'm going to put in S tier because the experience of this place is wonderful. Spotted Duck is an hour away, but it's known for t
```

6. Source: **Ranking 32 Collegetown Restaurants At Cornell University** (`ranking_32_collegetown_restaurants_at_cornell_university_6`) â€” YouTube review, Collegetown:

```
get freaking into this. Alright, so we have 32 restaurants to get through. These are order of closest to campus. CTB is definitely C tier. Everyone loves CTB because it's the hangout spot. They have a nice outdoor area. You can go there for food like sandwiches, subs, or you can just go there for a
```

7. Source: **Best-College-Food** (`best-college-food_48`) â€” the ranking blog (note the `23)` rank, used for comparison questions):

```
(Continued)
23)
Rice University
Rice University, located in Houston, Texas, ranks as having some of the best campus food because of their intentionality. The kitchens at Rice University strive to address food allergens and special dietary needs, halal and kosher dining, and plant-based eating. Chefs
```

---

## Retrieval test results

Run with `eval_retrieval.py` (top-k = 3, cosine distance; lower = more similar).

### Query 1: "What is the cost of the Bear Choice meal plan for undergraduates over 1 semester?"

| Rank | Distance  | Source                   | Chunk (excerpt)                                                                                                          |
| ---- | --------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| 1    | **0.211** | Undergraduate-Meal-Plans | "Bear Traditional - $3,400 per semesterâ€¦ **Bear Choice - $2,964 per semester**; $5,928 per year. Up to 10 meals peâ€¦" |
| 2    | 0.273     | Undergraduate-Meal-Plans | "â€¦unlimited meal swipesâ€¦ the plan includes Big Red Bucks (BRBs)â€¦ **Unlimited - $3,664 per semester**â€¦"           |
| 3    | 0.276     | Undergraduate-Meal-Plans | "â€¦(aka. Bear Supplemental) - $2,088.77 per semesterâ€¦ 127 meals per semesterâ€¦"                                      |

**Why these chunks are relevant:** All three come from the meal-plans document and list per-semester plan prices, which is exactly what the question asks about. The #1 chunk literally contains "Bear Choice - $2,964 per semester" â€” the exact expected answer â€” and its low distance (0.211) reflects a strong match. Chunks #2 and #3 are the neighboring plan tiers (Unlimited, Bear Supplemental); they're relevant context for a meal-plan cost question even though they aren't the specific plan asked about.

### Query 2: "What is the Spotted Duck sweet place known for?"

| Rank | Distance  | Source                                           | Chunk (excerpt)                                                                                                                                                                |
| ---- | --------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1    | **0.351** | Ranking 18 Sweet Pleasures At Cornell University | "**Spotted Duck is an hour away, but it's known for these ice cream flights where you can try a dozen flavors.** Now it's not ice cream, it's technically duck egg custardâ€¦" |
| 2    | 0.483     | Ranking 18 Sweet Pleasures At Cornell University | "â€¦to get a flight of itâ€¦ you are right next to the farm, so you see the ducks where they get the eggs fromâ€¦"                                                             |
| 3    | 0.489     | Ranking 18 Sweet Pleasures At Cornell University | "â€¦soft serve place. It's 20 minutes outâ€¦ Spotted Duck I'm going to put in S tier because the experience of this place is wonderfulâ€¦"                                     |

**Why these chunks are relevant:** All three are from the sweets-ranking transcript and are specifically about Spotted Duck. The #1 chunk answers the question directly ("known for these ice cream flights where you can try a dozen flavors" â€” the expected answer), and #2/#3 add supporting detail about the same place (the farm setting and its S-tier verdict). Semantic search found these even though the query word "known for" doesn't appear verbatim in #2/#3 â€” they match on the shared topic (Spotted Duck, flights, ice cream), which is what makes embedding-based retrieval useful here.

### Query 3: "Which general region of the Cornell campus is CafÃ© Jennie located?"

| Rank | Distance  | Source                                             | Chunk (excerpt)                                                                                                                                                        |
| ---- | --------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | **0.259** | Central - Cornell Dining Now                       | "â€¦**CafÃ© Jennie 10:00am â€“ 3:00pm (Central Campus)**. The Cornell Store Closed (Central Campus). A cafÃ© and sandwich/pastry shop located in The Cornell Storeâ€¦" |
| 2    | 0.329     | Ranking 62 Ithaca Restaurants For Cornell Students | "â€¦I graduated from Cornell University just this year. So I'm very familiar with all of the restaurants in the Ithaca areaâ€¦"                                        |
| 3    | 0.332     | Best-College-Food                                  | "â€¦Cornell Dining 'takes pride in providingâ€¦ a rich dining experience'â€¦ across their 29 campus eateriesâ€¦"                                                       |

**Why the top chunk is relevant (and why this query originally failed):** The #1 chunk names CafÃ© Jennie _and_ its campus together ("CafÃ© Jennieâ€¦ (Central Campus)"), so it directly answers the question â€” central campus. This only works because of a preprocessing fix: originally the chunk said CafÃ© Jennie was in "The Cornell Store" but never used the word "campus," so it didn't rank in the top 3, and the query instead matched chunks #2/#3 that merely mention "Cornell"/"campus" generically (note their higher, clustered distances of ~0.33). After tagging each eatery's name line with its campus during PDF extraction, the answer chunk jumped to #1 at distance 0.259. (See _Failure Case Analysis_ below for the full write-up.)

---

## Example responses

**Two Responses with source attribution visible in the output text**

CafÃ© Jennie is located on Central Campus. (Central - Cornell Dining Now)  
You can get ice cream at the Cornell Dairy Bar, which is located on campus. (source name) [1, 2, 3]

**One out-of-scope query showing the system's refusal response**
The loaded dining sources don't cover SUNY Buffalo meal plan. (source name)

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers

**Production tradeoff reflection:** all-MiniLM-L6-v2 is a small, fast, free and local model. The tradeoff is retrieval accuracy on domain text vs. latency/storage

---

## Grounded Generation

<!-- Explain how your system enforces grounding â€” how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" â€” show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** You are the Cornell Dining Guide, an assistant that answers questions about Cornell University dining â€” eateries, meal plans, hours, payment options, and where to eat around campus and Ithaca â€” by using only the provided context excerpts as your single source of truth, without relying on any outside knowledge or your own training, and you must either answer strictly from those excerpts (citing the source and, when comparing items, using any provided ranks or tiers as evidence), or if the context lacks sufficient information, state clearly that the loaded dining sources do not cover it, never inventing details, and at the end of every response, mention the source name if not already stated.

**How source attribution is surfaced in the response:** The system prompt requires that the answer be drawn strictly from the provided excerpts, explicitly cite the source, use any ranks or tiers as evidence when comparing items, and include the source name at the end of every response if not already mentioned earlier.

---

## Query interface

The interface is a Gradio chat app (`app.py`), launched with `python app.py`. On startup it ingests the documents into ChromaDB once (subsequent launches reuse the persisted store), then serves a chat UI in the browser.

**Input fields:**

- **Message textbox** â€” a single free-text field where the user types a natural-language dining question (e.g. "Where on campus is CafÃ© Jennie located?"). Submitting sends the message to the chat handler.
- **Example questions** â€” a set of clickable preset questions that populate the textbox, so the user can try the system without thinking one up.

**Output fields:**

- **Chat transcript** â€” a scrolling conversation view that shows each user message and the bot's grounded answer beneath it. Each answer is generated only from the retrieved chunks and ends with its source in `(source name)` form; if nothing relevant is found, it replies that the loaded dining sources don't cover the question.
- **Sidebar ("What I know about")** â€” a static panel listing the loaded source categories (campus eateries, meal plans, dining guide, student rankings, etc.) so the user knows the system's scope.

Under the hood each submitted message flows through `retrieve()` (embed query â†’ top-3 cosine search in ChromaDB) â†’ `generate_response()` (Groq `llama-3.3-70b-versatile` with the grounding prompt) â†’ the answer string rendered in the chat transcript.

**Sample interaction transcript:**

```
User:  What is the cost of the Bear Choice meal plan for one semester?

Cornell Dining Guide:
       The cost of the Bear Choice meal plan for one semester is $2,964.
       (Undergraduate-Meal-Plans)
```

This response was produced by the live system: retrieval returned the meal-plans chunk containing "Bear Choice - $2,964 per semester," and the model answered using only that excerpt and cited its source â€” matching the expected answer for evaluation question 1.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest â€” a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| #   | Question                                                                          | Expected answer                                                     | System response (summarized)                                                                                                                                                                                                                                                                                                       | Retrieval quality | Response accuracy |
| --- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | ----------------- |
| 1   | What is the cost of the Bear Choice meal plan for undergraduates over 1 semester? | $2,964                                                              | The Bear Choice meal plan costs $2,964 per semester. (source: Undergraduate-Meal-Plans [1])                                                                                                                                                                                                                                        | Relevant          | Accurate          |
| 2   | What is the Spotted Duck sweet place known for?                                   | It's known for ice cream flights where you can try a dozen flavors. | The Spotted Duck is known for its ice cream flights, where you can try a dozen flavors, but it's technically duck egg custard, not ice cream. (Ranking 18 Sweet Pleasures At Cornell University)                                                                                                                                   | Relevant          | Accurate          |
| 3   | Which general region of the Cornell campus is CafÃ© Jennie located?               | It's located in the central part of campus.                         | CafÃ© Jennie is located in the Central Campus region of the Cornell campus. (source: Central - Cornell Dining Now)                                                                                                                                                                                                                 | Relevant          | Accurate          |
| 4   | Is Cornell considered to have better food than Rice University?                   | Yes.                                                                | According to the rankings, Cornell University is ranked higher than Rice University. Cornell University is the first Ivy League university on the list, and Rice University is ranked 23rd. This implies that Cornell University is considered to have better food than Rice University, based on the ranking. (Best-College-Food) | Relevant          | Accurate          |
| 5   | Does Cornell provide reusable utensils? If so, where?                             | Yes. They are available to purchase at cafes.                       | Yes, Cornell provides reusable utensils. They are available to purchase at the cafes. (Guide-Cornell-Dining)                                                                                                                                                                                                                       | Relevant          | Accurate          |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context â€” the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "Which general region of the Cornell campus is CafÃ© Jennie located?" (expected: central campus)

**What the system returned:** Retrieval did not surface the chunk that actually describes CafÃ© Jennie. The top-3 results were an Ithaca-restaurant-ranking intro, a generic "Cornell Diningâ€¦ 29 eateries" blurb, and a guide chunk that happened to list _other_ cafÃ©s on North/West/Central Campus â€” none of which name CafÃ© Jennie. Their distances were high and tightly clustered (â‰ˆ0.329â€“0.337), the signature of no strong match. With no relevant context, the system could not give the correct "central campus" answer.

**Root cause (tied to a specific pipeline stage):** This is an **ingestion/embedding** failure (a vocabulary gap), not a generation one. The chunk that names CafÃ© Jennie comes from the `Central - Cornell Dining Now` PDF and reads "CafÃ© Jennieâ€¦ A cafÃ©â€¦ located in **The Cornell Store**" â€” it never contains the words "central campus." The campus region existed only in the PDF's _filename_, which is stored as metadata and is not part of the text the embedding model sees. So when the query asked about "region/campus," semantic search matched chunks that _literally_ contained "Central/North/West Campus" rather than the chunk that names the eatery, and the answer chunk fell outside the top-k.

**What you would change to fix it (done):** I updated `harvest_pdfs.py` to tag each eatery's name line with its campus â€” derived from the PDF filename â€” during extraction, e.g. `CafÃ© Jennie 10:00am â€“ 3:00pm (Central Campus)`. This puts the geography inside the chunk text where the embedding can use it, instead of leaving it stranded in metadata. After re-ingesting, the CafÃ© Jennie chunk became the **#1 result at distance 0.259** (down from 0.329, and previously absent from the top 3) and the system now answers "central campus" correctly. Alternative fixes considered: raising top-k from 3 to 5 to give the answer chunk more room to surface, or embedding the source/campus label alongside the chunk text at indexing time.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2â€“3 sentences each. -->

**One way the spec helped you during implementation:** The Chunking Strategy and Anticipated Challenges sections gave me a concrete checklist to verify against instead of just eyeballing output. In Chunking Strategy I had written that I'd know my chunks were too small "if retrieval returned a fragment with a rating but no restaurant name," so when I printed representative chunks I was specifically watching for that â€” and it showed up immediately, in a transcript chunk that read "The last time I went hereâ€¦" with the eatery's name stranded in the previous chunk. The Anticipated Challenges section had also predicted that the 25-college ranking blog and the point-in-time "Closed" PDFs would cause trouble, so I knew to watch for off-topic colleges and stale snapshots. Writing those failure modes down _before_ coding turned debugging into checking a list rather than discovering problems by surprise.

**One way your implementation diverged from the spec, and why:** My Documents table lists `now.dining.cornell.edu/eateries` as the source for the central/north/west eatery information, and I had planned to scrape it like my other web pages. In practice that site is a client-rendered (JavaScript) single-page app: a plain request returns an almost-empty HTML shell with none of the eatery names, hours, or descriptions, so my `harvest_pages.py` approach produced nothing usable. I diverged by capturing the rendered pages as PDFs (Central / North / West â€“ Cornell Dining Now) and extracting them with `pdfplumber` in a separate `harvest_pdfs.py`. That divergence then cascaded into changes I hadn't planned â€” stripping the site's nav/footer boilerplate from the PDF text and tagging each eatery with its campus â€” because the PDF carried UI chrome and dropped the campus context that the original URL structure had implied.

---

## Stretch Features — Conversational Memory

<!-- Demo or source showing a multi-turn exchange where the second query references
     context from the first, and the response reflects that memory — not just a
     coincidence of topic overlap. -->

The system supports conversational memory through two complementary mechanisms:

1. **Query rewriting** (`rewrite_query` in `generator.py`): Before retrieval, the follow-up question is passed to the LLM along with recent conversation history (up to 6 messages). The LLM rewrites elliptical queries — e.g. "What about on North campus?" → "What dining options are available on North campus?" — into a standalone search query that can retrieve relevant chunks on its own.

2. **Context injection** (`generate_response` in `generator.py`): After retrieval, the most recent conversation turns are replayed to the LLM as part of the message history. This lets the model resolve references like "it" or "that place" back to an eatery mentioned earlier, even when those names didn't survive the rewrite step.

The combination means the user can have a natural multi-turn conversation:

```
User:    Where is Café Jennie located?
AI:  Café Jennie is located on Central Campus. (Central - Cornell Dining Now)

User:    What about on North campus?
AI:  On North campus, there is Purcell Community Center. According to the information provided, it features various food options such as Chicken Sandwiches, Burgers, and more. (North - Cornell Dining Now)
```

In the second turn, `rewrite_query` expands "What about on North campus?" to something like "What dining options are available on North campus?" so retrieval looks for North Campus eateries rather than scattering on unrelated chunks. Then `generate_response` still sees the first turn in its history, so if the user had instead asked "What about there?" the model would know "there" refers to a specific eatery from the previous turn.

**Relevant source code:**

- `generator.py:_recent()` — caps history to the last 6 messages to bound token cost.
- `generator.py:rewrite_query()` — turns elliptical follow-ups into standalone search queries.
- `generator.py:generate_response()` — injects history as conversational context for the LLM.
- `app.py:chat()` — ties rewriting, retrieval, and generation together.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- _What I gave the AI:_ I asked AI harvest each dining cafe for me.
- _What it produced:_ The AI did harvest each dining cafe. Then I realized that each cafeâ€™s formatting was different, so I asked the AI (Groq) to analyze the raw HTML for me, but I was not satisfied with the result.
- _What I changed or overrode:_ Instead, I went to harvest the summary page of all cafes.

**Instance 2**

- _What I gave the AI:_ I asked AI why the bot can not answer question 'Is Cornell considered to have better food than Rice University?', Cornell in ranked #2 while Rice is ranked #23.
- _What it produced:_ AI tell me my system prompt is too strict. Since there is no direct compare between Cornell and Rice university, so AI can not give me an answer.
- _What I changed or overrode:_ I then changed the system prompt to use rank to compare.
