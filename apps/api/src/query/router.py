from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from db.postgres.models.user import User
from db.postgres.session import get_db

from .schemas import QueryRequest, QueryResponse
from .service import QueryService

router = APIRouter(prefix="/query", tags=["query"])

@router.post("/", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Single-turn RAG query. Ask a question against one or more uploaded documents.
    Returns the answer and the source chunks used to generate it.
    """
    return await QueryService(db).query(
        question=request.question,
        document_ids=request.document_ids,
        top_k=request.top_k,
    )
