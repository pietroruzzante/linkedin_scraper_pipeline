from pypdf import PdfReader

def parse_cv(cv_path) -> str:
    reader = PdfReader(cv_path)
    return "".join(page.extract_text() or "" for page in reader.pages)