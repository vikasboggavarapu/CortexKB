from config import get_settings

settings = get_settings()

def chunk_text(
    text:str,
    chunk_size:int | None = None,
    chunk_overlap : int | None = None,
) -> list[str]:

  """
  Split text into overlapping chunks by character count.
  Returns a list of non empty chunk settings
 
  """
  size = chunk_size or settings.chunk_size
  overlap = chunk_overlap or settings.chunk_overlap

  if not text.strip():
    return []

  chunks: list[str] = []
  start = 0

  while start < len(text):
    end = start + size
    chunk = text[start:end].strip()
    if chunk:
        chunks.append(chunk)
    if end >= len(text):
        break
    start += size - overlap

  return chunks      