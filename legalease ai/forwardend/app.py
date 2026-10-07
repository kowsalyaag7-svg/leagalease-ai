import html
import os
from datetime import date

import requests
import streamlit as st


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .subtitle {
        text-align: center;
        color: #777;
        margin-bottom: 30px;
    }

    .preview-card {
        background: #111827;
        color: #f9fafb;
        padding: 28px;
        border-radius: 12px;
        max-height: 650px;
        overflow-y: auto;
        line-height: 1.7;
        border: 1px solid #374151;
    }

    .preview-card h1,
    .preview-card h2,
    .preview-card h3 {
        color: #ffffff;
    }

    .warning-box {
        padding: 14px;
        border-radius: 8px;
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #7c2d12;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Header
left, center, right = st.columns(
    [1, 2, 1]
)

with center:
    logo_path = os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
        "assets",
        "logo.png",
    )

    if os.path.exists(logo_path):
        st.image(
            logo_path,
            width=100,
        )

    st.markdown(
        '<div class="main-title">LegalEase</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        "AI-Assisted Legal Document Generator"
        "</div>",
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="warning-box">
    <strong>Important:</strong> LegalEase creates AI-assisted drafts.
    Review the generated document carefully and obtain qualified legal
    advice before relying on it for a legal matter.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")


# Session state
if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""

if "editing" not in st.session_state:
    st.session_state.editing = False


# Input area
st.subheader("Create a legal document")

document_type = st.selectbox(
    "Document type",
    [
        "Employment Contract",
        "Non-Disclosure Agreement (NDA)",
        "Residential Lease Agreement",
        "Freelance Work Contract",
        "Service Agreement",
        "Employment Offer Letter",
        "Partnership Agreement",
        "General Agreement",
        "Custom Legal Document",
    ],
)

custom_type = ""

if document_type == "Custom Legal Document":
    custom_type = st.text_input(
        "Specify document type",
        placeholder="Example: Software Development Agreement",
    )

    if custom_type.strip():
        document_type = custom_type.strip()


parties = st.text_area(
    "Parties involved",
    placeholder=(
        "Example:\n"
        "Jane Doe (Service Provider)\n"
        "TechNova Inc. (Client)"
    ),
    height=130,
)


terms = st.text_area(
    "Terms & Conditions",
    placeholder=(
        "Enter each term separated by a semicolon.\n\n"
        "Payment within 30 days of invoice; "
        "Provider will deliver work by agreed deadline; "
        "Confidential information must remain protected; "
        "Either party may terminate with 15 days notice"
    ),
    height=180,
)


effective_date = st.date_input(
    "Effective date",
    value=date.today(),
)


additional_instructions = st.text_area(
    "Additional instructions (optional)",
    placeholder=(
        "Example: Use a formal tone and include "
        "signature blocks for both parties."
    ),
    height=100,
)


generate = st.button(
    "Generate Document",
    type="primary",
    use_container_width=True,
)


if generate:
    if not parties.strip():
        st.error("Please enter the parties involved.")

    elif not terms.strip():
        st.error("Please enter the terms and conditions.")

    else:
        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date.isoformat(),
            "additional_instructions": additional_instructions,
        }

        with st.spinner(
            "Generating your legal document..."
        ):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=180,
                )

                if response.ok:
                    data = response.json()

                    st.session_state.generated_text = (
                        data["content"]
                    )

                    st.session_state.editing = False

                    st.success(
                        "Document generated successfully."
                    )

                else:
                    try:
                        detail = response.json().get(
                            "detail",
                            response.text,
                        )
                    except Exception:
                        detail = response.text

                    st.error(
                        f"Backend error: {detail}"
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to FastAPI. "
                    "Make sure the backend is running on "
                    f"{BACKEND_URL}."
                )

            except Exception as exc:
                st.error(
                    f"Unexpected error: {exc}"
                )


# Generated document
if st.session_state.generated_text:
    st.divider()

    st.subheader("Generated Document")

    edit_col, status_col = st.columns(
        [1, 3]
    )

    with edit_col:
        if st.button(
            "Edit Document",
            use_container_width=True,
        ):
            st.session_state.editing = True

    with status_col:
        if st.session_state.editing:
            st.info(
                "Edit the document below and click Save Changes."
            )

    if st.session_state.editing:

        edited_text = st.text_area(
            "Editable document",
            value=st.session_state.generated_text,
            height=650,
        )

        if st.button(
            "Save Changes",
            type="primary",
        ):
            st.session_state.generated_text = edited_text
            st.session_state.editing = False

            st.success(
                "Changes saved."
            )

            st.rerun()

    else:
        preview = html.escape(
            st.session_state.generated_text
        )

        preview = preview.replace(
            "\n",
            "<br>",
        )

        st.markdown(
            f"""
            <div class="preview-card">
                {preview}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.subheader("Download")

    download_cols = st.columns(3)

    content = st.session_state.generated_text

    for col, fmt, label in zip(
        download_cols,
        ["txt", "docx", "pdf"],
        ["Download TXT", "Download DOCX", "Download PDF"],
    ):
        with col:
            if st.button(
                label,
                use_container_width=True,
            ):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/export",
                        json={
                            "document_type": document_type,
                            "content": content,
                            "format": fmt,
                        },
                        timeout=60,
                    )

                    if response.ok:
                        mime_types = {
                            "txt": "text/plain",
                            "docx": (
                                "application/vnd.openxmlformats-officedocument."
                                "wordprocessingml.document"
                            ),
                            "pdf": "application/pdf",
                        }

                        extensions = {
                            "txt": "txt",
                            "docx": "docx",
                            "pdf": "pdf",
                        }

                        st.download_button(
                            label=(
                                f"Save {fmt.upper()} file"
                            ),
                            data=response.content,
                            file_name=(
                                f"legalease_document."
                                f"{extensions[fmt]}"
                            ),
                            mime=mime_types[fmt],
                            use_container_width=True,
                        )

                    else:
                        try:
                            detail = response.json().get(
                                "detail",
                                response.text,
                            )
                        except Exception:
                            detail = response.text

                        st.error(
                            f"Export failed: {detail}"
                        )

                except Exception as exc:
                    st.error(
                        f"Export error: {exc}"
                    )


st.divider()

st.caption(
    "LegalEase • AI-assisted document drafting • "
    "Review all generated content before use"
)