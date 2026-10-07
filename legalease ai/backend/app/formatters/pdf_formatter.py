from io import BytesIO
from pathlib import Path
import re

from fpdf import FPDF

from backend.app.utils.text import sanitize_text


ASSET_DIR = Path(__file__).resolve().parents[3] / "assets"
LOGO_PATH = ASSET_DIR / "logo.png"


class LegalEasePDF(FPDF):

    def __init__(self, document_type: str):
        super().__init__()

        self.document_type = document_type

        self.set_auto_page_break(
            auto=True,
            margin=20,
        )

    def header(self):
        if LOGO_PATH.exists():
            try:
                self.image(
                    str(LOGO_PATH),
                    x=95,
                    y=8,
                    w=20,
                )
            except Exception:
                pass

        self.set_y(32)

        self.set_font(
            "Times",
            "B",
            13,
        )

        self.cell(
            0,
            8,
            self.document_type,
            align="C",
        )

        self.ln(10)

    def footer(self):
        self.set_y(-15)

        self.set_font(
            "Times",
            "",
            8,
        )

        self.cell(
            0,
            5,
            "LegalEase - AI-assisted legal document draft",
            align="C",
        )

        self.ln(4)

        self.cell(
            0,
            5,
            f"Page {self.page_no()}",
            align="C",
        )


def _write_line(pdf: FPDF, line: str):
    line = line.strip()

    if not line:
        pdf.ln(3)
        return

    if re.match(r"^\d+\.\s+", line):
        pdf.set_font(
            "Times",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            line,
        )

        pdf.set_font(
            "Times",
            "",
            11,
        )

    elif line.startswith(("-", "•", "*")):
        cleaned = re.sub(
            r"^[-•*]\s*",
            "",
            line,
        )

        pdf.set_font(
            "Times",
            "",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            f"- {cleaned}",
        )

    else:
        pdf.set_font(
            "Times",
            "",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            line,
        )


def format_pdf(text: str, doc_type: str) -> bytes:
    text = sanitize_text(text)

    pdf = LegalEasePDF(
        document_type=doc_type,
    )

    pdf.set_title(doc_type)

    pdf.add_page()

    for block in text.split("\n\n"):
        for line in block.splitlines():
            _write_line(
                pdf,
                line,
            )

        pdf.ln(2)

    raw = pdf.output()

    if isinstance(raw, bytes):
        return raw

    return bytes(raw)