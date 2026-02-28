import asyncio
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_user
from config import settings
from connection_manager import manager
from database import get_db
from models import PendingFile, User

router = APIRouter(prefix="/files", tags=["files"])

FILE_TTL_HOURS = 24 * 7  # 7 days


class FileOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    original_filename: str
    stored_filename: str
    part_number: int
    total_parts: int
    comment: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


@router.post("/upload", response_model=FileOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    receiver_id: int = Form(...),
    original_filename: str = Form(...),
    part_number: int = Form(1),
    total_parts: int = Form(1),
    comment: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    receiver = db.get(User, receiver_id)
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")

    # Create DB record first to get the id
    record = PendingFile(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        original_filename=original_filename,
        stored_filename="",  # filled after we know the id
        part_number=part_number,
        total_parts=total_parts,
        comment=comment,
        status="pending",
    )
    db.add(record)
    db.flush()  # assigns record.id without committing

    relative_path = f"{record.id}/part_{part_number}"
    record.stored_filename = relative_path

    dest_dir = settings.STORAGE_PATH / str(record.id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = settings.STORAGE_PATH / relative_path

    async with aiofiles.open(dest_file, "wb") as f:
        while chunk := await file.read(1024 * 256):  # 256 KB chunks
            await f.write(chunk)

    db.commit()
    db.refresh(record)

    # Notify receiver via WebSocket
    asyncio.create_task(
        manager.send_to_user(
            receiver_id,
            {
                "event": "new_file",
                "file_id": record.id,
                "sender": current_user.username,
                "original_filename": original_filename,
                "part_number": part_number,
                "total_parts": total_parts,
            },
        )
    )

    return record


@router.get("/pending", response_model=list[FileOut])
def list_pending(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(PendingFile)
        .filter(
            PendingFile.receiver_id == current_user.id,
            PendingFile.status == "pending",
        )
        .all()
    )


@router.get("/{file_id}/part/{part_n}")
def download_part(
    file_id: int,
    part_n: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record: PendingFile | None = (
        db.query(PendingFile)
        .filter(PendingFile.id == file_id, PendingFile.part_number == part_n)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if record.receiver_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    path = settings.STORAGE_PATH / record.stored_filename
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not on disk")

    return FileResponse(
        path=str(path),
        filename=record.original_filename,
        media_type="application/octet-stream",
    )


@router.post("/{file_id}/ack", status_code=status.HTTP_204_NO_CONTENT)
async def ack_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record: PendingFile | None = db.get(PendingFile, file_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if record.receiver_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    record.status = "delivered"
    db.commit()

    dir_path = settings.STORAGE_PATH / str(record.id)
    asyncio.create_task(_delete_dir(dir_path))


async def _delete_dir(path: Path) -> None:
    await asyncio.sleep(0)  # yield to event loop
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


async def cleanup_expired_files(db_factory) -> None:
    """Background task: mark and delete files older than TTL."""
    while True:
        try:
            await asyncio.sleep(3600)  # run every hour
            cutoff = datetime.now(timezone.utc) - timedelta(hours=FILE_TTL_HOURS)
            db: Session = db_factory()
            try:
                expired = (
                    db.query(PendingFile)
                    .filter(
                        PendingFile.status == "pending",
                        PendingFile.created_at < cutoff,
                    )
                    .all()
                )
                for rec in expired:
                    rec.status = "expired"
                    dir_path = settings.STORAGE_PATH / str(rec.id)
                    if dir_path.exists():
                        shutil.rmtree(dir_path, ignore_errors=True)
                db.commit()
            finally:
                db.close()
        except asyncio.CancelledError:
            break
        except Exception:
            pass  # don't let cleanup crash the server
