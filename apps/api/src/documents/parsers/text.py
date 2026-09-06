from .base import BaseParser

class TextParser(BaseParser):
    def parse(self,content:bytes) -> str:
        return content.decode("utf-8",errors="replace").strip()