import pathlib
import re

import tinycss2
from bs4 import BeautifulSoup

import check50

HTML_FILES_COUNT = 4
HTML_TAGS_REQUIRED = 7
CSS_SELECTORS_REQUIRED = 5
CSS_FEATURES_REQUIRED = 5
STYLES_CSS = "styles.css"


def get_html_files():
    return [f for f in pathlib.Path(".").iterdir() if f.is_file() and f.suffix == ".html"]


@check50.check()
def html_files_exist():
    """📂\tHTML-Dateien existieren."""
    html_files = get_html_files()
    if len(html_files) != HTML_FILES_COUNT:
        raise check50.Failure(f"Expected {HTML_FILES_COUNT} HTML files, found {len(html_files)}")
    if not any(f.name.lower() == "index.html" for f in html_files):
        raise check50.Failure("Missing index.html")


@check50.check()
def html_linking():
    """🔗\tHTML Dateien korrekt untereinander verlinkt."""
    html_files = get_html_files()
    if len(html_files) != HTML_FILES_COUNT:
        raise check50.Failure(f"Expected {HTML_FILES_COUNT} HTML files, found {len(html_files)}")

    html_names = [f.name for f in html_files]
    links = {f.name: set() for f in html_files}

    for html_file in html_files:
        content = html_file.read_text(encoding="utf-8")
        soup = BeautifulSoup(content, "html.parser")
        for a_tag in soup.find_all("a", href=True) + soup.find_all("a", class_="nav-link", href=True):
            href = a_tag["href"].split("#")[0]
            if href in html_names:
                links[html_file.name].add(href)

    for name in html_names:
        expected_links = set(html_names) - {name}
        if not expected_links.issubset(links[name]):
            raise check50.Failure(f"HTML file {name} does not link to all other HTML files.")


@check50.check()
def html_tag_usage():
    """📄\tMindestens sieben verschiedede HTML-Tags verwendet"""
    all_tags = set()
    for html_file in get_html_files():
        content = html_file.read_text(encoding="utf-8")
        soup = BeautifulSoup(content, "html.parser")
        all_tags.update(tag.name for tag in soup.find_all())
    all_tags -= {"html", "head", "body", "title"}
    if len(all_tags) < HTML_TAGS_REQUIRED:
        raise check50.Failure(f"Not enough different HTML tags used (found {len(all_tags)})")


@check50.check()
def css_file_exists():
    """📄\tCSS Datei styles.css existiert"""
    check50.exists(STYLES_CSS)


@check50.check()
def css_file_included():
    """📄\tCSS Datei korrekt eingebunden."""
    css_path = pathlib.Path(STYLES_CSS)
    for file in get_html_files():
        content = file.read_text(encoding="utf-8")
        soup = BeautifulSoup(content, "html.parser")
        for link_tag in soup.find_all("link", rel="stylesheet", href=True):
            href = pathlib.Path(link_tag["href"])
            if str(href) in str(css_path):
                return
    raise check50.Failure("CSS file not linked in any HTML files.")


@check50.check()
def css_selectors_used():
    """📄\tMindestens 5 verschiedene CSS-Selektoren in styles.css verwendet."""
    css_path = pathlib.Path(STYLES_CSS)
    try:
        content = css_path.read_text(encoding="utf-8")
        rules = tinycss2.parse_stylesheet(content, skip_comments=True, skip_whitespace=True)
    except Exception as e:
        raise check50.Failure(f"Error reading or parsing CSS file: {e}")

    selectors = set()
    for rule in rules:
        if rule.type == "qualified-rule":
            prelude = tinycss2.serialize(rule.prelude).strip()
            if prelude:
                selectors.add(prelude)

    if len(selectors) < CSS_SELECTORS_REQUIRED:
        raise check50.Failure(f"Not enough unique CSS selectors (found {len(selectors)})")


@check50.check()
def css_features_used():
    """📄\tMindestens 5 verschiedene CSS-Eigenschaften in styles.css verwendet."""
    css_path = pathlib.Path(STYLES_CSS)
    try:
        content = css_path.read_text(encoding="utf-8")
        rules = tinycss2.parse_stylesheet(content, skip_comments=True, skip_whitespace=True)
    except Exception as e:
        raise check50.Failure(f"Error reading or parsing CSS file: {e}")

    properties = set()
    for rule in rules:
        if rule.type == "qualified-rule":
            for decl in tinycss2.parse_declaration_list(rule.content):
                if decl.type == "declaration":
                    properties.add(decl.lower_name)

    if len(properties) < CSS_FEATURES_REQUIRED:
        raise check50.Failure(f"Not enough unique CSS features (found {len(properties)})")


@check50.check()
def bootstrap_included():
    """📦\tBootstrap korrekt eingebunden.."""
    bootstrap_cdn_pattern = re.compile(
        r"(https://cdn\.jsdelivr\.net/npm/bootstrap[^\"'\s]*|https://stackpath\.bootstrapcdn\.com/bootstrap[^\"'\s]*)",
        re.I,
    )
    for html_file in get_html_files():
        content = html_file.read_text(encoding="utf-8")
        soup = BeautifulSoup(content, "html.parser")
        for link_tag in soup.find_all(["link", "script"], href=True):
            if bootstrap_cdn_pattern.findall(link_tag["href"]):
                return
        for script_tag in soup.find_all("script", src=True):
            if bootstrap_cdn_pattern.findall(script_tag["src"]):
                return
    raise check50.Failure("Bootstrap not included")


@check50.check()
def bootstrap_used():
    """📄\tMindestens ein Bootstrap Feature auf der Webseite integriert."""
    bootstrap_classes = ["container", "row", "col", "btn", "navbar", "alert", "card", "modal"]
    for html_file in get_html_files():
        content = html_file.read_text(encoding="utf-8")
        soup = BeautifulSoup(content, "html.parser")
        for class_name in bootstrap_classes:
            if soup.select(f".{class_name}"):
                return
    raise check50.Failure("Bootstrap CDN not used or no Bootstrap components found.")
