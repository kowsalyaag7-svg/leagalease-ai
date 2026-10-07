from backend.app.utils.text import sanitize_text


def format_txt(text: str, doc_type: str = "") -> bytes:
    cleaned = sanitize_text(text)

    if doc_type:
        header = f"{doc_type}\n{'=' * len(doc_type)}\n\n"
        cleaned = header + cleaned

    return cleaned.encode("utf-8")