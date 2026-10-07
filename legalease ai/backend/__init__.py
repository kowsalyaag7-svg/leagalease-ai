import html
import re
from typing import List


def sanitize_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def parse_terms(terms: str) -> List[str]:
    return [
        item.strip()
        for item in terms.split(";")
        if item.strip()
    ]


def escape_html(text: str) -> str:
    return html.escape(
        text,
        quote=True,
    )


def safe_filename(value: str) -> str:
    value = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        value.strip(),
    )

    value = value.strip("._")

    return value[:80] or "legalease_document"