"""
harvest_pages.py — Harvest plain web pages into the documents/ folder.

Unlike harvest.py (which uses Groq to extract structured About/Accept/Hours
from the dining API), these are ordinary server-rendered HTML pages, so we
just grab the page and pull out its readable content:

  - <slug>.txt  : the extracted, cleaned plain text (ready for RAG ingestion)

Usage:
  python harvest_pages.py
  python harvest_pages.py "https://example.com/page" "https://example.com/two"
"""

import os
import re
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

OUT_DIR = "documents"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

URLS = [
    "https://www.collegetransitions.com/blog/best-college-food/",
    "https://scl.cornell.edu/residential-life/dining/about-dining/guide-cornell-dining",
    "https://scl.cornell.edu/residential-life/dining/meal-plans-rates/undergraduate-meal-plans",
]


def slug_from_url(url):
    """Build a filesystem-safe slug from the URL's last meaningful path part."""
    path = urlparse(url).path.rstrip("/")
    name = path.split("/")[-1] or urlparse(url).netloc
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)


def extract_text(html):
    """Pull readable text out of an HTML page, dropping boilerplate."""
    soup = BeautifulSoup(html, "html.parser")

    # Strip elements that never carry article content.
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer",
                     "form", "svg", "iframe"]):
        tag.decompose()

    # Prefer the main/article region if the page marks one up.
    main = soup.find("main") or soup.find("article") or soup.body or soup
    title = soup.title.get_text(strip=True) if soup.title else ""

    text = main.get_text(separator="\n")
    # Collapse runs of blank lines and trailing whitespace.
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    body = "\n".join(lines)
    return title, body


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    urls = sys.argv[1:] or URLS
    os.makedirs(OUT_DIR, exist_ok=True)

    for url in urls:
        slug = slug_from_url(url)
        print(f"Fetching {url} ...")
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        html = resp.text

        # Extracted text.
        title, body = extract_text(html)
        txt_path = os.path.join(OUT_DIR, slug + ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"{title}\nSource: {url}\n\n{body}\n")

        print(f"  -> {txt_path}  ({len(body):,} chars text)")

    print(f"\nDone. Harvested {len(urls)} page(s) -> ./{OUT_DIR}/")


if __name__ == "__main__":
    main()
