# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

I chose dining at Cornell University as my domain. This knowledge is valuable to those dining at Cornell, especially newly admitted students who are unfamiliar with the situation. This knowledge in some cases can be found on Cornell's official websites, but this isn't always the case: For instance, YouTube videos about rankings of dining places would normally require a user to watch through parts of the video to get the information and explanations they need, which can be time consuming as it requires finding the video and clicking around to the right moment in the video.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| #   | Source           | Description                                                    | URL or location                                                                           |
| --- | ---------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1   | Blog             | Overview of food rankings across colleges and universities.    | https://www.collegetransitions.com/blog/best-college-food/                                |
| 2   | Official Website | Dining options in central Cornell campus.                      | https://now.dining.cornell.edu/eateries                                                   |
| 3   | YouTube Video    | Ranking of all Cornell restaurant options.                     | https://www.youtube.com/watch?v=oXL7lPaCTFQ                                               |
| 4   | YouTube Video    | Ranking of all places in Cornell for sweets.                   | https://www.youtube.com/watch?v=hR9lBcRT1pc                                               |
| 5   | YouTube Video    | Ranking of many places in the Finger Lakes region for food.    | https://www.youtube.com/watch?v=5qamJiAfKQI                                               |
| 6   | Official Website | A general guide to dining and dining options at Cornell.       | https://scl.cornell.edu/residential-life/dining/about-dining/guide-cornell-dining         |
| 7   | YouTube Video    | Ranking of many Ithaca dining options.                         | https://www.youtube.com/watch?v=v47vqblonJo                                               |
| 8   | Official Website | Dining options in north Cornell campus.                        | https://now.dining.cornell.edu/eateries                                                   |
| 9   | Official Website | Various meal plans for undergraduate students; includes costs. | https://scl.cornell.edu/residential-life/dining/meal-plans-rates/undergraduate-meal-plans |
| 10  | Official Website | Dining options in west Cornell campus.                         | https://now.dining.cornell.edu/eateries                                                   |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 300

**Overlap:** 50

**Reasoning:** Although the text files are of different formats, they all consist of a certain place and then a few sentences describing that place, so a constant chunk size should be able to successfully capture each place.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 3

**Production tradeoff reflection:** all-MiniLM-L6-v2 is a small, fast, free and local model. The tradeoff is retrieval accuracy on domain text vs. latency/storage

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question                                                                          | Expected answer                                                     |
| --- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| 1   | What is the cost of the Bear Choice meal plan for undergraduates over 1 semester? | $2,964                                                              |
| 2   | What is the Spotted Duck sweet place known for?                                   | It's known for ice cream flights where you can try a dozen flavors. |
| 3   | Which general region of the Cornell campus is Café Jennie located?                | It's located in the central part of campus.                         |
| 4   | Is Cornell considered to have better food than Rice University?                   | Yes.                                                                |
| 5   | Does Cornell provide reusable utensils? If so, where?                             | Yes. They are available to purchase at cafes.                       |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
