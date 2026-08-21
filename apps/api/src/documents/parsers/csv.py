import io
import csv

from .base import BaseParser

class CSVParser(BaseParser):
    def parse(self,content:bytes) -> str:
        text = content.decode("utf-8",errors="replace")
        reader = csv.reader(io.StringIO(text))
        rows = [", ".join(row) for row in reader  if any(cell.strip() for cell in row)]
        return "\n".join(rows).strip()