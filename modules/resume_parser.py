"""
modules/resume_parser.py
Extracts text from PDF/DOCX and splits into labelled sections.
"""
import re
import io
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# ── Section detection patterns ──────────────────────────────────────────────
SECTION_PATTERNS = {
    "summary":        r"\b(summary|objective|profile|about|overview)\b",
    "education":      r"\b(education|academic|qualification|degree|university|college|b\.?tech|m\.?tech|bachelor|master|ph\.?d)\b",
    "experience":     r"\b(experience|work|employment|internship|career|position|responsibilities)\b",
    "skills":         r"\b(skills|technologies|tools|proficient|expertise|competencies|technical)\b",
    "projects":       r"\b(projects|portfolio|built|developed|created|implemented)\b",
    "certifications": r"\b(certifications?|certified|certificate|license|credential|achievement)\b",
}

# ── Text extraction ─────────────────────────────────────────────────────────

def _extract_pdf_pdfminer(data: bytes) -> str:
    from pdfminer.high_level import extract_text
    from pdfminer.layout import LAParams
    return extract_text(io.BytesIO(data), laparams=LAParams(line_margin=0.5)) or ""

def _extract_pdf_pymupdf(data: bytes) -> str:
    import fitz
    doc = fitz.open(stream=data, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def extract_text_from_pdf(data: bytes) -> str:
    try:
        text = _extract_pdf_pdfminer(data)
        if text.strip():
            return text
    except Exception as e:
        logger.warning(f"pdfminer failed ({e}), falling back to PyMuPDF")
    try:
        return _extract_pdf_pymupdf(data)
    except Exception as e:
        logger.error(f"PyMuPDF also failed: {e}")
        return ""

def extract_text_from_docx(data: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

# ── Text cleaning ───────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)          # strip HTML
    text = re.sub(r"[^\x00-\x7F]+", " ", text)    # remove non-ASCII
    text = re.sub(r"[ \t]{2,}", " ", text)         # collapse spaces
    text = re.sub(r"\n{3,}", "\n\n", text)         # max 2 blank lines
    return text.strip()

# ── Section detection ────────────────────────────────────────────────────────

def detect_sections(text: str) -> Dict[str, str]:
    sections = {k: "" for k in SECTION_PATTERNS}
    sections["other"] = ""
    lines = text.split("\n")
    current = "other"
    buffer = []

    for line in lines:
        stripped = line.strip()
        matched = False
        if stripped and len(stripped) < 60:
            for sec, pat in SECTION_PATTERNS.items():
                if re.search(pat, stripped, re.IGNORECASE):
                    if sec != current:
                        sections[current] += "\n".join(buffer) + "\n"
                        current = sec
                        buffer = []
                        matched = True
                    break
        if not matched:
            buffer.append(line)

    sections[current] += "\n".join(buffer)
    return {k: v.strip() for k, v in sections.items()}

# ── Contact extraction ───────────────────────────────────────────────────────

def extract_contact(text: str) -> Dict[str, str]:
    info = {}
    # Email
    m = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
    if m:
        info["email"] = m.group()
    # Phone
    m = re.search(r"(\+?91[-.\s]?\d{10}|\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\d{10})", text)
    if m:
        info["phone"] = m.group().strip()
    # LinkedIn
    m = re.search(r"linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
    if m:
        info["linkedin"] = "https://" + m.group()
    # GitHub
    m = re.search(r"github\.com/[\w-]+", text, re.IGNORECASE)
    if m:
        info["github"] = "https://" + m.group()
    # Name heuristic (first non-empty short line)
    for line in text.split("\n"):
        line = line.strip()
        if 2 < len(line) < 50 and not re.search(r"[@/:|]|resume|curriculum", line, re.IGNORECASE):
            info["name"] = line
            break
    return info

# ── Main entry point ─────────────────────────────────────────────────────────

def parse_resume(file_bytes: bytes, file_type: str) -> Dict:
    """
    Parse a resume file and return structured data.

    Args:
        file_bytes : raw bytes of the uploaded file
        file_type  : 'pdf' or 'docx'

    Returns:
        {raw_text, sections, contact_info, word_count, char_count}
        or {error: str} on failure
    """
    ext = file_type.lower().strip(".")
    if ext == "pdf":
        raw = extract_text_from_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        raw = extract_text_from_docx(file_bytes)
    else:
        return {"error": f"Unsupported file type: {file_type}"}

    if not raw.strip():
        return {"error": "Could not extract text. Please try a different file."}

    clean = clean_text(raw)
    return {
        "raw_text":    clean,
        "sections":    detect_sections(clean),
        "contact_info": extract_contact(clean),
        "word_count":  len(clean.split()),
        "char_count":  len(clean),
    }
