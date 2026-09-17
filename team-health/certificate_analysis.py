"""Shared certificate-analysis logic for the team-health assignment.

Used by both __init__.py (the check50 checks students run) and the
teacher-side review_team_health_certificates.py script -- one place that
knows what a genuine vhb "Flourishing Together" certificate looks like,
imported by both instead of duplicated.

The certificate is a TCPDF-generated PDF from the vhb OPEN course platform.
Content checks (course title, completion statement) are meant to be hard
failures -- there's no legitimate reason a real certificate would fail
them. Tamper signals are NOT meant to be hard failures: they're heuristics
about how PDF editors behave (see detect_tamper_signals' docstring), with
a real (if unlikely) false-positive risk, so callers should report them
rather than block a student's score on them.
"""

import re
import unicodedata

import pypdf

EXPECTED_COURSE_TITLE = (
    "Flourishing Together: Strengthening Team Health and "
    "Collaboration in Hybrid and Virtual Work"
)
EXPECTED_COMPLETION_STATEMENT = (
    "The online self-tests required to issue this certificate have been passed."
)
EXPECTED_PRODUCER_SUBSTRING = "TCPDF"

# Between "Certificate of Participation" and "has successfully participated"
# sits exactly one line: the participant's name.
NAME_PATTERN = re.compile(
    r"Certificate of Participation\s*\n(.+?)\s*\nhas successfully participated",
    re.DOTALL,
)
DOWNLOAD_DATE_PATTERN = re.compile(
    r"This certificate has been downloaded on (\d{2}/\d{2}/\d{4})"
)


def load(pdf_path):
    """Reads the PDF once; returns (reader, text, error). error is a
    human-readable string if the file couldn't be read as a PDF at all
    (missing, empty, corrupted, encrypted, or an image-only scan with no
    extractable text), None otherwise."""
    try:
        reader = pypdf.PdfReader(pdf_path)
        if reader.is_encrypted:
            return reader, None, "is password-protected, cannot be read"
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:  # noqa: BLE001 -- any failure here means "not a valid PDF"
        return None, None, f"could not be read as a PDF ({e})"

    if not text.strip():
        return reader, "", "contains no extractable text (looks like a scanned image, not the real download)"

    return reader, text, None


def _normalize_whitespace(s):
    # The course title wraps across two lines in the PDF itself (a real
    # newline lands mid-title in the extracted text), so an exact-substring
    # match needs both sides collapsed to single spaces first.
    return re.sub(r"\s+", " ", s).strip()


def validate_content(text):
    """Returns a list of content problems (empty = a genuine, complete
    certificate for this course). Hard-failure material."""
    normalized = _normalize_whitespace(text)
    problems = []
    if _normalize_whitespace(EXPECTED_COURSE_TITLE) not in normalized:
        problems.append("does not contain the expected course title -- wrong certificate uploaded?")
    if _normalize_whitespace(EXPECTED_COMPLETION_STATEMENT) not in normalized:
        problems.append("does not show the self-tests as passed -- looks incomplete")
    return problems


def extract_display_info(text):
    """Best-effort extraction of the participant name and download date,
    for human review -- never gates anything, since the exact wording
    around these could shift and shouldn't fail an otherwise-valid cert."""
    name_match = NAME_PATTERN.search(text)
    date_match = DOWNLOAD_DATE_PATTERN.search(text)
    return {
        "name": name_match.group(1).strip() if name_match else None,
        "downloaded_on": date_match.group(1) if date_match else None,
    }


def detect_tamper_signals(pdf_path, reader):
    """Returns a list of human-readable tamper signals (empty = clean).

    Three checks, all based on how PDF editors behave, not on this
    specific file's content:

    1. Producer metadata: TCPDF stamps every certificate it generates.
       Re-saving through any other tool (Preview.app, Acrobat, an online
       editor, a Word/LibreOffice export) rewrites this field to that
       tool's own signature.
    2. CreationDate == ModDate: TCPDF sets both identically at generation
       time. Nothing in a normal "download my certificate" flow touches
       ModDate afterward -- any tool that resaves the file changes this.
    3. Single PDF generation: a pristine, never-resaved PDF has exactly
       one trailer/xref/%%EOF and no /Prev key. Acrobat's default "Save"
       (as opposed to "Save As") does an *incremental* update -- appends a
       new generation onto the original bytes rather than rewriting the
       file -- which is exactly what this catches.

    None of this is cryptographic proof of authenticity -- a forger who
    reads this file and knows to fake the Producer string while doing a
    full clean rewrite defeats it. It raises the bar against casual
    editing, which is the realistic threat model here.
    """
    signals = []

    meta = reader.metadata or {}
    producer = str(meta.get("/Producer", ""))
    if EXPECTED_PRODUCER_SUBSTRING not in producer:
        signals.append(f'Producer mismatch (found "{producer or "none"}", expected to contain "TCPDF")')

    creation_date = meta.get("/CreationDate")
    mod_date = meta.get("/ModDate")
    if creation_date != mod_date:
        signals.append(f"CreationDate ({creation_date}) differs from ModDate ({mod_date})")

    with open(pdf_path, "rb") as f:
        raw = f.read()
    if raw.count(b"%%EOF") > 1 or raw.count(b"startxref") > 1 or b"/Prev" in raw:
        signals.append("PDF has more than one generation (looks like it was opened and re-saved)")

    return signals


def _normalize_name_token(s):
    # Same conservative approach as lab-attendance's nameMatching.js: fold
    # case/whitespace/diacritics (this is real extracted text, not OCR, so
    # no digit-confusion folding is needed here).
    s = re.sub(r"\s+", " ", s.strip().lower())
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def names_plausibly_match(certificate_name, roster_first_name, roster_last_name):
    """True if both roster name parts appear among the certificate name's
    tokens (order-independent, so "Nachname Vorname" vs "Vorname Nachname"
    both work). False if either roster part is missing entirely -- there's
    nothing meaningful to compare. This is NOT used at grade time (no
    roster access there, see module docstring) -- it's for the teacher-side
    review script, which does have real roster data from scores.csv."""
    if not certificate_name or not roster_first_name or not roster_last_name:
        return None

    cert_tokens = set(_normalize_name_token(certificate_name).split(" "))
    return (
        _normalize_name_token(roster_first_name) in cert_tokens
        and _normalize_name_token(roster_last_name) in cert_tokens
    )
