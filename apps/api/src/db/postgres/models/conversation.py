from datetime import datetime

from sqlalchemy import String,DateTime,ForeignKey

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from ..session import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id:Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


    title:Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    created_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )


    user = relationship(
        "User",
        back_populates="comversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all,delete-orphan"
    )