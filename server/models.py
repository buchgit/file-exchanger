from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer, String, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    force_change_password: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    sent_files: Mapped[list["PendingFile"]] = relationship(
        "PendingFile", foreign_keys="PendingFile.sender_id", back_populates="sender"
    )
    received_files: Mapped[list["PendingFile"]] = relationship(
        "PendingFile", foreign_keys="PendingFile.receiver_id", back_populates="receiver"
    )


class PendingFile(Base):
    __tablename__ = "pending_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    receiver_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    part_number: Mapped[int] = mapped_column(Integer, default=1)
    total_parts: Mapped[int] = mapped_column(Integer, default=1)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    sender: Mapped["User"] = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_files"
    )
    receiver: Mapped["User"] = relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_files"
    )

