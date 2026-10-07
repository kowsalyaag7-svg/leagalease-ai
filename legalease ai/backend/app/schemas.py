from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Type of legal document to generate.",
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=5000,
        description="People or entities involved in the document.",
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=10000,
        description="Terms and conditions.",
    )

    effective_date: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Effective date of the document.",
    )

    additional_instructions: Optional[str] = Field(
        default="",
        max_length=10000,
        description="Optional additional drafting instructions.",
    )

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "effective_date",
        mode="before",
    )
    @classmethod
    def strip_required_fields(cls, value):
        if value is None:
            return value

        value = str(value).strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value

    @field_validator("additional_instructions", mode="before")
    @classmethod
    def clean_optional_instructions(cls, value):
        if value is None:
            return ""

        return str(value).strip()


class GenerateResponse(BaseModel):
    success: bool
    document_type: str
    content: str


class ExportRequest(BaseModel):
    document_type: str
    content: str
    format: str