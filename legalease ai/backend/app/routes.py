from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.app.ai_core.gemini_generator import (
    GeminiDocumentGenerator,
)
from backend.app.formatters.docx_formatter import (
    format_docx,
)
from backend.app.formatters.pdf_formatter import (
    format_pdf,
)
from backend.app.formatters.txt_formatter import (
    format_txt,
)
from backend.app.schemas import (
    DocumentRequest,
    ExportRequest,
    GenerateResponse,
)
from backend.app.utils.text import sanitize_text


router = APIRouter(
    prefix="",
    tags=["LegalEase"],
)


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "LegalEase",
    }


@router.post(
    "/generate",
    response_model=GenerateResponse,
)
def generate_document(
    request: DocumentRequest,
):
    try:
        generator = GeminiDocumentGenerator()

        content = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
            additional_instructions=request.additional_instructions,
        )

        return GenerateResponse(
            success=True,
            document_type=request.document_type,
            content=content,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document generation failed: {exc}",
        ) from exc


@router.post("/export")
def export_document(
    request: ExportRequest,
):
    content = sanitize_text(
        request.content
    )

    document_type = (
        request.document_type.strip()
        or "Legal Document"
    )

    export_format = (
        request.format.strip().lower()
    )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Document content cannot be empty.",
        )

    if export_format == "txt":
        data = format_txt(
            content,
            document_type,
        )

        return Response(
            content=data,
            media_type="text/plain",
            headers={
                "Content-Disposition": (
                    'attachment; filename="legalease_document.txt"'
                )
            },
        )

    if export_format == "docx":
        data = format_docx(
            content,
            document_type,
        )

        return Response(
            content=data,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            headers={
                "Content-Disposition": (
                    'attachment; filename="legalease_document.docx"'
                )
            },
        )

    if export_format == "pdf":
        data = format_pdf(
            content,
            document_type,
        )

        return Response(
            content=data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    'attachment; filename="legalease_document.pdf"'
                )
            },
        )

    raise HTTPException(
        status_code=400,
        detail=(
            "Unsupported format. "
            "Use txt, docx, or pdf."
        ),
    )