import io

from docx import Document

from .base import BaseParser

class DocxParser(BaseParser):
    def parse(self,content : bytes) -> str:
        doc = Document(io.BytesIO(content))
        paragraphs = [p.text  for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()