"""
harvest_pdfs.py — Extract text from the PDFs in pdf/ and save each as a .txt
document in documents/, ready for the RAG ingestion pipeline.

Usage:
  python harvest_pdfs.py
  python harvest_pdfs.py "pdf/Some File.pdf"
"""

import glob
import os
import re
import sys

import pdfplumber

PDF_DIR = "pdf"
OUT_DIR = "documents"

# These PDFs are print-outs of the "Cornell Dining Now" web app, so every page
# carries the site's navigation chrome and footer — text that has no dining
# content but pollutes the chunks/embeddings. We drop these exact lines
# (matched case-insensitively after stripping).
NAV_LINES = {
    "add funds",
    "cornell dining now",
    "eateries eatery map feedback netnutrition about",
    "dining room prices",
    "eateries",
    "select date",
    "open dining nearest",
    "search",
    "today rooms first",
    "all central north west",
}

# The date-picker value, e.g. "Sunday, June 7, 2026" — a point-in-time nav
# artifact, not dining info.
_DATE_RE = re.compile(
    r"^(mon|tues|wednes|thurs|fri|satur|sun)day,\s+\w+\s+\d{1,2},\s+\d{4}$", re.I
)
# Private-use-area code points (U+E000–U+F8FF) are icon-font glyphs (e.g. the
# "Closed" status icon) that extract as garbage characters.
_PUA_RE = re.compile("[-]")


# The campus region is in the filename ("Central/North/West - Cornell Dining
# Now") but not in the chunk text, so a query like "which campus is Café Jennie
# on?" can't match the eatery's chunk. We tag each eatery's name/status line
# with its campus so the geography rides along into the embedding.
_CAMPUS = {"central": "Central Campus", "north": "North Campus", "west": "West Campus"}
# An eatery name line ends with its status ("Closed") or carries hours
# ("10:00am – 3:00pm"); description and "Featuring:" lines do neither.
_EATERY_LINE_RE = re.compile(r"\d{1,2}:\d{2}\s*[ap]m", re.I)


def slug_from_path(path):
    """Filesystem-safe slug from a PDF filename (no extension)."""
    base = os.path.splitext(os.path.basename(path))[0]
    return re.sub(r"[^A-Za-z0-9._-]", "_", base).strip("_")


def _campus_from_path(path):
    """Map 'Central - Cornell Dining Now.pdf' -> 'Central Campus' (or None)."""
    base = os.path.basename(path).lower()
    for key, label in _CAMPUS.items():
        if base.startswith(key):
            return label
    return None


def _is_eatery_line(line):
    """True for an eatery's name/status line (vs. description/Featuring lines)."""
    low = line.strip().lower()
    return low.endswith("closed") or bool(_EATERY_LINE_RE.search(low))


def _is_boilerplate(line):
    """True if a line is site nav/footer chrome rather than dining content."""
    low = line.strip().lower()
    if not low:
        return True
    if low in NAV_LINES:
        return True
    if _DATE_RE.match(low):
        return True
    if low.startswith("©") or "cornell university - student and campus life" in low:
        return True
    if low.startswith("if you have a disability") or "web-accessibility@cornell.edu" in low:
        return True
    return False


def extract_pdf(path):
    """Return the concatenated text of every page, with site chrome removed."""
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    text = "\n".join(pages)
    text = _PUA_RE.sub("", text)  # drop icon-font glyphs

    campus = _campus_from_path(path)

    cleaned = []
    for ln in text.splitlines():
        ln = ln.rstrip()
        if not ln.strip() or _is_boilerplate(ln):
            continue
        # Tag each eatery's name line with its campus so the geography is
        # embedded with the eatery (e.g. "Café Jennie ... (Central Campus)").
        if campus and _is_eatery_line(ln):
            ln = f"{ln} ({campus})"
        cleaned.append(ln)
    return "\n".join(cleaned)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(PDF_DIR, "*.pdf")))
    if not paths:
        sys.exit(f"No PDFs found in ./{PDF_DIR}/")

    os.makedirs(OUT_DIR, exist_ok=True)

    for path in paths:
        name = os.path.splitext(os.path.basename(path))[0]
        print(f"Extracting {path} ...")
        body = extract_pdf(path)
        out_path = os.path.join(OUT_DIR, slug_from_path(path) + ".txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"{name}\nSource: {path}\n\n{body}\n")
        print(f"  -> {out_path}  ({len(body):,} chars)")

    print(f"\nDone. Extracted {len(paths)} PDF(s) -> ./{OUT_DIR}/")


if __name__ == "__main__":
    main()
