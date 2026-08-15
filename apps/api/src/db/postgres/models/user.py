from datetime import datetime

from sqlalchemy import String,DateTime
from sqlalchemy.orm import Mapped,mapped_column,relationship

from ..session import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    email:Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password:Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    role:Mapped[str] = mapped_column(
        String(50),
        nullable = False,
        default= "user"
    )

    created_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )

    documents = relationship(
        "Document",
        back_populates="uploader"
    )

    conversations = relationship(
        "Conversation",
        back_populates="user"
    )