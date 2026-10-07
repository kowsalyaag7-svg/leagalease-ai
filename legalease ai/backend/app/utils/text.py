import html
import re


def sanitize_text(text: str) -> str:
    """
    Clean AI-generated text before sending it to document formatters.
    """

    if not text:
        return ""

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

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove accidental null characters.
    text = text.replace("\x00", "")

    # Normalize excessive blank lines.
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    return text.strip()


def escape_html(text: str) -> str:
    return html.escape(text)


def text_to_html(text: str) -> str:
    """
    Convert generated plain text into safe HTML for Streamlit preview.
    """

    safe = escape_html(sanitize_text(text))

    paragraphs = safe.split("\n\n")

    output = []

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        lines = paragraph.split("\n")

        rendered_lines = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("- "):
                rendered_lines.append(
                    f"<li>{stripped[2:]}</li>"
                )
            else:
                rendered_lines.append(
                    stripped
                )

        if any(line.startswith("<li>") for line in rendered_lines):
            output.append(
                "<ul>" + "".join(rendered_lines) + "</ul>"
            )
        else:
            output.append(
                "<p>" + "<br>".join(rendered_lines) + "</p>"
            )

    return "\n".join(output)