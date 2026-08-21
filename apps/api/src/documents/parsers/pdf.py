import io

from pypdf import PdfReader

from .base import BaseParser

class PDFParser(BaseParser):
    def parse(self,content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()