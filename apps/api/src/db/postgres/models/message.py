from datetime import datetime
from typing import Any

from sqlalchemy import String,DateTime,ForeignKey,Text
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from ..session import Base

class Message(Base):

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
     )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    sources: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    








conversation = relationship(
    "Conversation",
    back_populates="messages"
)