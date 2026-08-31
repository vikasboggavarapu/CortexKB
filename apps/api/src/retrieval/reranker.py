from dataclasses import dataclass

from .semantic import SemanticResult
from .keyword import KeywordResult

@dataclass
class RankedChunk:
    document_id: int
    text:str
    score: float
    source : str

def rerank(
    semantic_results : list[SemanticResult],
    keyword_results : list[KeywordResult],
    top_k : int = 5,
) -> list[RankedChunk]:

   K = 60
   scores: dict[str,dict] = {}

   for rank,result in enumerate(semantic_results,start=1):
    key = f"{result.document_id}_{result.chunk_index}"
    if key not in scores:
        scores[key] = {
            "document_id": result.document_id,
            "text": result.text,
            "score" : 0.0,
            "source": set(),
        }
    scores[key]["score"] += 1 / (K + rank)
    scores[key]["source"].add("semantic")
   for rank,result in enumerate(keyword_results,start = 1):
    key = f"{result.document_id}_keyword"
    if key not in scores:
        scores[key] = {
            "document_id": result.document_id,
            "text" : result.text,
            "score": 0.0,
            "source":set(),
        }        
    scores[key]["score"] += 1 / (K + rank)
    scores[key]["source"].add("keyword")
   
   ranked = sorted(scores.values(),key = lambda x: x["score"],reverse=True)
   return [
      RankedChunk(
        document_id=item["document_id"],
        text=item["text"],
        score=round(item["score"],6),
        source="+".join(sorted(item["source"])),
      )
      for item in ranked[:top_k]
   ]


