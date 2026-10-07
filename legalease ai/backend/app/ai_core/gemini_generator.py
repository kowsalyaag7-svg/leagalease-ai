from google import genai
from google.genai import types

from backend.app.config import settings
from backend.app.utils.text import sanitize_text


class GeminiDocumentGenerator:
    """
    Gemini-powered legal document generator.

    The generated material is intended as an AI-assisted draft and
    should be reviewed by a qualified legal professional before use.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your .env file."
            )

        self.client = genai.Client(api_key=self.api_key)

    def build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        additional_instructions: str = "",
    ) -> str:

        return f"""
You are an expert legal drafting assistant.

Create a structured legal document based on the information below.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

EFFECTIVE DATE:
{effective_date}

TERMS AND CONDITIONS:
{terms}

ADDITIONAL INSTRUCTIONS:
{additional_instructions or "None"}

IMPORTANT DRAFTING RULES:

1. Produce a professional legal-document draft.
2. Do not invent names, addresses, monetary amounts, dates,
   jurisdictions, obligations, or facts that were not provided.
3. Where important information is missing, use a clear placeholder
   such as [INSERT INFORMATION].
4. Organize the document with a title and numbered sections.
5. Clearly identify the parties.
6. Include the effective date.
7. Convert the supplied terms into appropriate contractual clauses.
8. Include standard provisions only when appropriate to the document.
9. Avoid claiming that the document is guaranteed legally valid.
10. Do not provide explanations outside the document.
11. Return plain text suitable for editing and DOCX/PDF conversion.

Recommended structure:

TITLE

PARTIES / INTRODUCTION

1. PURPOSE
2. DEFINITIONS
3. OBLIGATIONS
4. PAYMENT / CONSIDERATION, if applicable
5. CONFIDENTIALITY, if applicable
6. TERM AND TERMINATION
7. REPRESENTATIONS AND WARRANTIES, if appropriate
8. LIABILITY / INDEMNIFICATION, if appropriate
9. GOVERNING LAW, using [INSERT JURISDICTION] if not supplied
10. DISPUTE RESOLUTION, if appropriate
11. GENERAL PROVISIONS
12. SIGNATURES

Only include sections relevant to the document type.

Generate the complete draft now.
""".strip()

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        additional_instructions: str = "",
    ) -> str:

        prompt = self.build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
            additional_instructions=additional_instructions,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=8000,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return sanitize_text(response.text)