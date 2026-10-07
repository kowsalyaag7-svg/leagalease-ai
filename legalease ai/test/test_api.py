from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "LegalEase"
    assert data["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_txt_export():
    response = client.post(
        "/export",
        json={
            "document_type": "NDA",
            "content": "This is a confidentiality agreement.",
            "format": "txt",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "text/plain"
    )

    assert (
        b"This is a confidentiality agreement."
        in response.content
    )


def test_docx_export():
    response = client.post(
        "/export",
        json={
            "document_type": "NDA",
            "content": "Confidentiality obligations.",
            "format": "docx",
        },
    )

    assert response.status_code == 200

    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats"
    )

    assert len(response.content) > 100


def test_pdf_export():
    response = client.post(
        "/export",
        json={
            "document_type": "NDA",
            "content": "Confidentiality obligations.",
            "format": "pdf",
        },
    )

    assert response.status_code == 200

    assert response.headers["content-type"].startswith(
        "application/pdf"
    )

    assert response.content.startswith(
        b"%PDF"
    )


@patch(
    "backend.app.routes.GeminiDocumentGenerator"
)
def test_generate(mock_generator):
    mock_instance = mock_generator.return_value

    mock_instance.generate_document.return_value = (
        "NON-DISCLOSURE AGREEMENT\n\n"
        "1. CONFIDENTIALITY\n"
        "The parties agree to protect confidential information."
    )

    response = client.post(
        "/generate",
        json={
            "document_type": "NDA",
            "parties": "Alice (Disclosing Party), Bob (Receiving Party)",
            "terms": (
                "Confidentiality must be maintained; "
                "Either party may terminate with 15 days notice"
            ),
            "effective_date": "2026-09-30",
            "additional_instructions": "",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["document_type"] == "NDA"
    assert "CONFIDENTIALITY" in data["content"]