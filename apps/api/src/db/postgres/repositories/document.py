from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.document import Document
from .base import BaseRepository


class DocumentRepository(BaseRepository[Document]):

    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)

    async def create(
        self,
        filename: str,
        file_type: str,
        uploaded_by: int,
        status: str = "uploaded",
        chroma_collection_id: str | None = None,
    ) -> Document:

        document = Document(
            filename=filename,
            file_type=file_type,
            uploaded_by=uploaded_by,
            status=status,
            chroma_collection_id=chroma_collection_id,
        )

        self.session.add(document)

        await self.session.commit()
        await self.session.refresh(document)

        return document

    async def get_by_user(
        self,
        user_id: int,
    ) -> list[Document]:

        result = await self.session.execute(
            select(Document)
            .where(Document.uploaded_by == user_id)
            .order_by(Document.created_at.desc())
        )

        return list(result.scalars().all())

    async def update_status(
        self,
        document_id: int,
        status: str,
    ) -> Document | None:

        document = await self.get(document_id)

        if document is None:
            return None

        document.status = status

        await self.session.commit()
        await self.session.refresh(document)

        return document