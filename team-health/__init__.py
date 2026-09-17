import glob
import os
import sys

import check50

# check50's loader execs this file directly rather than importing it as a
# real package member, so a relative import (`from . import ...`) fails --
# add this folder to sys.path explicitly instead.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import certificate_analysis as ca


def find_pdf():
    """The single PDF file in the submission's root directory (any
    filename -- students aren't required to name it a specific way), or
    None if there isn't exactly one. Non-recursive on purpose: a PDF
    buried in some unrelated subfolder shouldn't count."""
    pdfs = sorted(glob.glob("*.pdf"))
    return pdfs[0] if len(pdfs) == 1 else None


@check50.check()
def exists():
    """📁\tPDF gefunden"""
    pdfs = sorted(glob.glob("*.pdf"))
    if not pdfs:
        raise check50.Failure("keine PDF-Datei im Repository gefunden")
    if len(pdfs) > 1:
        raise check50.Failure(f"mehrere PDF-Dateien gefunden ({', '.join(pdfs)}) -- bitte nur eine hochladen")


@check50.check(exists)
def is_valid_pdf():
    """📄\tPDF ist eine gültige, lesbare Datei"""
    pdf_path = find_pdf()
    _reader, _text, err = ca.load(pdf_path)
    if err:
        raise check50.Failure(f"{pdf_path} {err}")


@check50.check(is_valid_pdf)
def correct_course():
    """✅\tZertifikat für den richtigen Kurs, vollständig abgeschlossen"""
    _reader, text, _err = ca.load(find_pdf())
    problems = ca.validate_content(text)
    if problems:
        raise check50.Failure("; ".join(problems))


@check50.check(is_valid_pdf)
def integrity_review():
    """🔍\tZertifikat-Integrität"""
    pdf_path = find_pdf()
    reader, text, _err = ca.load(pdf_path)
    info = ca.extract_display_info(text)
    signals = ca.detect_tamper_signals(pdf_path, reader)

    check50.log(f"Name auf dem Zertifikat: {info['name']}")
    check50.log(f"Heruntergeladen am: {info['downloaded_on']}")
    if signals:
        for signal in signals:
            check50.log(f"⚠ {signal}")
    else:
        check50.log("Keine Auffälligkeiten gefunden.")

    # Never raises check50.Failure -- always passes. Tamper signals are
    # heuristics about PDF-editor behaviour, not proof, so they're surfaced
    # here (and picked up later by review_team_health_certificates.py) for
    # a human to judge, never used to block a student's score. See
    # certificate_analysis.detect_tamper_signals' docstring for why.
    check50.data(name=info["name"], downloaded_on=info["downloaded_on"], tamper_signals=signals)
