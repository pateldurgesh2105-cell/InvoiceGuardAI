from pathlib import Path
import fitz


def extract_pdf_text(pdf_path: str) -> str:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(pdf_path)
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc).strip()
