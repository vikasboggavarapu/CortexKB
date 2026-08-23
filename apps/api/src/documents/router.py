from typing import Annotated

from fastapi import APIRouter,Depends,UploadFile,File,status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from db.postgres.models.user import User
from db.postgres.session import get_db

from .schemas import DocumentListResponse,DocumentResponse
from .service import DocumentService

router = APIRouter(prefix= "/documents",tags=["documents"])

@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: Annotated[UploadFile,File(description="PDF, DOCX, CSV, or TXT file")],
    current_user : Annotated[User,Depends(get_current_user)],
    db: Annotated[AsyncSession,Depends(get_db)],
):
  return await DocumentService(db).upload(file,current_user.id)

@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await DocumentService(db).list_documents(current_user.id)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await DocumentService(db).delete(document_id, current_user.id)
