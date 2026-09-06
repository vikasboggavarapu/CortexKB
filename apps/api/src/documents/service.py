import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres.repositories.document import DocumentRepository
from db.vector.chroma import delete_document_collection, upsert_document_chunks
from llm.embeddings import embed_texts

from .chunker import chunk_text
from .parsers.csv import CSVParser
from .parsers.docs import DocxParser
from .parsers.pdf import PDFParser
from .parsers.text import TextParser
from .schemas import DocumentListResponse, DocumentResponse

# Map MIME types and extensions to parsers
PARSERS = {
    "application/pdf": PDFParser(),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocxParser(),
    "text/csv": CSVParser(),
    "text/plain": TextParser(),
}

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".csv", ".txt"}

def _get_parser(filename: str, content_type: str):
    # Try by MIME type first, fall back to extension
    if content_type in PARSERS:
        return PARSERS[content_type]
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    extension_map = {
        ".pdf": PDFParser(),
        ".docx": DocxParser(),
        ".csv": CSVParser(),
        ".txt": TextParser(),
    }
    if ext in extension_map:
        return extension_map[ext]
    return None

class DocumentService:

    def __init__(self, session: AsyncSession):
        self.repo = DocumentRepository(session)

    async def upload(self, file: UploadFile, user_id: int) -> DocumentResponse:
        # Validate extension
        ext = "." + file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        parser = _get_parser(file.filename or "", file.content_type or "")
        if parser is None:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Could not determine file parser.",
            )

        # Create DB record with status=processing
        collection_id = f"doc_{uuid.uuid4().hex}"
        document = await self.repo.create(
            filename=file.filename or "unknown",
            file_type=ext.lstrip("."),
            uploaded_by=user_id,
            status="processing",
            chroma_collection_id=collection_id,
        )

        try:
            content = await file.read()
            text = parser.parse(content)

            if not text.strip():
                await self.repo.update_status(document.id, "failed")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Could not extract text from the uploaded file.",
                )

            chunks = chunk_text(text)
            embeddings = await embed_texts(chunks)
            await upsert_document_chunks(collection_id, chunks, embeddings, document.id)

            document = await self.repo.update_status(document.id, "ready")

        except HTTPException:
            raise
        except Exception as exc:
            await self.repo.update_status(document.id, "failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document processing failed: {str(exc)}",
            ) from exc

        return DocumentResponse.model_validate(document)

    async def list_documents(self, user_id: int) -> DocumentListResponse:
        docs = await self.repo.get_by_user(user_id)
        return DocumentListResponse(
            documents=[DocumentResponse.model_validate(d) for d in docs],
            total=len(docs),
        )

    async def delete(self, document_id: int, user_id: int) -> None:
        document = await self.repo.get(document_id)

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )
        if document.uploaded_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this document.",
            )

        if document.chroma_collection_id:
            await delete_document_collection(document.chroma_collection_id)

        await self.repo.delete(document_id)
