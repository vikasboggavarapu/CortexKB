from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from ..session import Base


class Document(Base):
    __tablename__ = "Document"
    id:Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )


    filename:Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_type:Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    status:Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="uploaded"
    )

    uploaded_by:Mapped[int] = mapped_column(
        ForeignKey("users.id" ,ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=true),
        nullable=False,
        default=datetime.utcnow
    )

    chroma_collection_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable = Truec
    )


    uploader = relationship(
        "User",
        back_populates="documents"
    )