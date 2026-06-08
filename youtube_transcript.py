"""
youtube_transcript.py — Download YouTube video transcripts and save each as a
plain-text document, ready for the RAG ingestion pipeline.

Usage:
  python youtube_transcript.py            # harvests every URL in URLS
  python youtube_transcript.py "https://www.youtube.com/watch?v=oXL7lPaCTFQ" ...
"""

import os
import re
import sys
from urllib.parse import urlparse, parse_qs

import requests
from youtube_transcript_api import YouTubeTranscriptApi

OUT_DIR = "documents"

URLS = [
    "https://www.youtube.com/watch?v=oXL7lPaCTFQ",
    "https://www.youtube.com/watch?v=hR9lBcRT1pc",
    "https://www.youtube.com/watch?v=5qamJiAfKQI",
    "https://www.youtube.com/watch?v=v47vqblonJo",
]


def video_id_from_url(url):
    """Extract the 11-char video id from a watch/youtu.be/shorts/embed URL."""
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/")
    if "v" in parse_qs(parsed.query):
        return parse_qs(parsed.query)["v"][0]
    # /shorts/<id> or /embed/<id>
    parts = [p for p in parsed.path.split("/") if p]
    if parts:
        return parts[-1]
    raise SystemExit(f"Could not parse a video id from URL: {url}")


def fetch_title(video_id):
    """Look up the video title/author via YouTube's oEmbed endpoint."""
    try:
        data = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"},
            timeout=20,
        ).json()
        return data.get("title"), data.get("author_name")
    except Exception:
        return None, None


def fetch_transcript(video_id):
    """Return the transcript snippets for the video."""
    ytt = YouTubeTranscriptApi()
    return ytt.fetch(video_id).snippets


def safe_filename(text, fallback):
    """Turn a title into a filesystem-safe .txt filename."""
    if not text:
        return f"{fallback}.txt"
    name = re.sub(r"[^A-Za-z0-9._ -]", "", text).strip().replace(" ", "_")
    name = name[:80].strip("_") or fallback
    return f"{name}.txt"


def harvest_one(url):
    """Download one video's transcript and save it to OUT_DIR."""
    video_id = video_id_from_url(url)
    print(f"Video id: {video_id}")

    title, author = fetch_title(video_id)
    print(f"Title: {title!r}  Author: {author!r}")

    print("Fetching transcript ...")
    snippets = fetch_transcript(video_id)
    print(f"  - {len(snippets)} snippets")

    # Join the snippet text into clean paragraphs.
    body = " ".join(s.text.replace("\n", " ").strip() for s in snippets)
    body = re.sub(r"\s+", " ", body).strip()

    header = (
        f"{title or 'YouTube Transcript'}\n"
        f"Source: {url}\n"
        f"Channel: {author or 'Unknown'}\n\n"
        "Transcript:\n"
    )

    filename = safe_filename(title, video_id)
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + body + "\n")
    print(f"  -> saved {path}  ({len(body):,} chars)")


def main():
    # The Windows console is cp1252 and chokes on emoji/accents in titles.
    # Make all prints tolerant; the .txt file is always written as UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    urls = sys.argv[1:] or URLS
    os.makedirs(OUT_DIR, exist_ok=True)

    for url in urls:
        harvest_one(url)

    print(f"\nDone. Harvested {len(urls)} transcript(s) -> ./{OUT_DIR}/")


if __name__ == "__main__":
    main()
