"""Shared certificate-analysis logic for the ai-drivers-license assignment.

Used by both __init__.py (the check50 checks students run) and the
teacher-side review script -- one place that knows what a genuine
"Regensburger KI-Führerschein" certificate looks like, imported by both
instead of duplicated.

The certificate is a pdf-lib-generated PDF (https://www.ki-regensburg.de).
Note this uses pymupdf, not pypdf (unlike team-health's certificate_analysis.py):
pypdf and pdfplumber both fail or are non-deterministic on this specific
file's structure (a compressed-xref-stream PDF with a stamped-on name text
run that has no reliable ToUnicode mapping under those two libraries) --
confirmed by repeated testing before writing this module. pymupdf extracts
both text and metadata correctly and reproducibly.

Content checks (course title, completion statement) are meant to be hard
failures -- there's no legitimate reason a real certificate would fail
them. Tamper signals are NOT meant to be hard failures: they're heuristics
about how PDF editors behave (see detect_tamper_signals' docstring), with
a real (if unlikely) false-positive risk, so callers should report them
rather than block a student's score on them.
"""

import re
import unicodedata

import pymupdf

EXPECTED_COURSE_TITLE = "Regensburger KI‑Führerschein"
EXPECTED_COMPLETION_STATEMENT = (
    "hat das E‑Learning „Regensburger KI‑Führerschein“ erfolgreich abgeschlossen."
)
EXPECTED_PRODUCER_SUBSTRING = "pdf-lib"

# The recipient's name is stamped onto the template as the very last text
# run on the page (confirmed by inspecting real extracted text -- it comes
# out *after* the signature block in reading order, not where it visually
# sits on the page), so it's extracted positionally: everything after the
# fixed "Stadt Regensburg" signature line, to the end of the page text.
NAME_PATTERN = re.compile(r"Stadt Regensburg\s*\n(.+?)\s*$", re.DOTALL)


def load(pdf_path):
    """Reads the PDF once; returns (doc, text, error). error is a
    human-readable string if the file couldn't be read as a PDF at all
    (missing, empty, corrupted, encrypted, or an image-only scan with no
    extractable text), None otherwise."""
    try:
        doc = pymupdf.open(pdf_path)
        if doc.is_encrypted:
            return doc, None, "is password-protected, cannot be read"
        if doc.page_count < 1:
            return doc, None, "has no pages"
        text = doc[0].get_text()
    except Exception as e:  # noqa: BLE001 -- any failure here means "not a valid PDF"
        return None, None, f"could not be read as a PDF ({e})"

    if not text.strip():
        return doc, "", "contains no extractable text (looks like a scanned image, not the real download)"

    return doc, text, None


def _normalize_name_token(s):
    s = re.sub(r"\s+", " ", s.strip().lower())
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def validate_content(text):
    """Returns a list of content problems (empty = a genuine, complete
    certificate for this course). Hard-failure material."""
    problems = []
    if EXPECTED_COURSE_TITLE not in text:
        problems.append("does not contain the expected course title -- wrong certificate uploaded?")
    if EXPECTED_COMPLETION_STATEMENT not in text:
        problems.append("does not show the course as successfully completed -- looks incomplete")
    return problems


def extract_display_info(text):
    """Best-effort extraction of the participant name, for human review --
    never gates anything, since a positional heuristic like this could
    shift if the certificate template ever changes and shouldn't fail an
    otherwise-valid cert."""
    name_match = NAME_PATTERN.search(text)
    return {"name": name_match.group(1).strip() if name_match else None}


def names_plausibly_match(certificate_name, roster_first_name, roster_last_name):
    """True if both roster name parts appear among the certificate name's
    tokens (order-independent). False if either roster part is missing
    entirely -- there's nothing meaningful to compare. Not used at grade
    time (no roster access there) -- for the teacher-side review script."""
    if not certificate_name or not roster_first_name or not roster_last_name:
        return None

    cert_tokens = set(_normalize_name_token(certificate_name).split(" "))
    return (
        _normalize_name_token(roster_first_name) in cert_tokens
        and _normalize_name_token(roster_last_name) in cert_tokens
    )


def detect_tamper_signals(pdf_path, doc):
    """Returns a list of human-readable tamper signals (empty = clean).

    Three checks, all based on how PDF editors behave, not on this
    specific file's content:

    1. Producer/Creator metadata: pdf-lib stamps every certificate this
       platform generates. Re-saving through any other tool (a PDF editor,
       an online tool, a print-to-PDF step) rewrites this field to that
       tool's own signature.
    2. CreationDate == ModDate: set identically at generation time; nothing
       in a normal download flow touches ModDate afterward.
    3. Single PDF generation: a pristine, never-resaved PDF has exactly one
       trailer/xref/%%EOF and no /Prev key, even with this PDF's compressed
       xref-stream structure (verified directly: the final startxref/%%EOF
       trailer wrapper is always plain text, even when the xref table
       itself is compressed) -- an incrementally-updated file (e.g.
       Acrobat's default "Save") appends a second one.

    None of this is cryptographic proof of authenticity -- a forger who
    reads this file and knows to fake the Producer string while doing a
    full clean rewrite defeats it. It raises the bar against casual
    editing, which is the realistic threat model here.
    """
    signals = []

    meta = doc.metadata or {}
    producer = meta.get("producer", "") or ""
    if EXPECTED_PRODUCER_SUBSTRING not in producer:
        signals.append(f'Producer mismatch (found "{producer or "none"}", expected to contain "pdf-lib")')

    creation_date = meta.get("creationDate")
    mod_date = meta.get("modDate")
    if creation_date != mod_date:
        signals.append(f"CreationDate ({creation_date}) differs from ModDate ({mod_date})")

    with open(pdf_path, "rb") as f:
        raw = f.read()
    if raw.count(b"%%EOF") > 1 or raw.count(b"startxref") > 1 or b"/Prev" in raw:
        signals.append("PDF has more than one generation (looks like it was opened and re-saved)")

    return signals
