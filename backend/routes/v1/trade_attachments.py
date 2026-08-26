from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from database.database import get_db

from dependencies.auth import (
    get_current_user,
)

from models.trade import Trade
from models.trade_attachment import (
    TradeAttachment,
)
from models.user import User

from schemas.trade_attachment import (
    TradeAttachmentListResponse,
    TradeAttachmentResponse,
)


router = APIRouter(
    prefix="/trades",
    tags=["Trade Attachments"],
)


UPLOAD_ROOT = Path(
    "uploads/trades"
)

UPLOAD_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)


ALLOWED_IMAGE_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
}

ALLOWED_PDF_TYPES = {
    "application/pdf",
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
}


def get_owned_trade(
    db: Session,
    user_id: int,
    trade_id: int,
) -> Trade:
    trade = (
        db.query(Trade)
        .filter(
            Trade.id == trade_id,
            Trade.user_id == user_id,
        )
        .first()
    )

    if trade is None:
        raise HTTPException(
            status_code=404,
            detail="Trade not found.",
        )

    return trade


def get_owned_attachment(
    db: Session,
    user_id: int,
    trade_id: int,
    attachment_id: int,
) -> TradeAttachment:
    attachment = (
        db.query(TradeAttachment)
        .filter(
            TradeAttachment.id == attachment_id,
            TradeAttachment.trade_id == trade_id,
            TradeAttachment.user_id == user_id,
        )
        .first()
    )

    if attachment is None:
        raise HTTPException(
            status_code=404,
            detail="Attachment not found.",
        )

    return attachment


def detect_attachment_type(
    mime_type: str | None,
) -> str:
    mime_type = (
        mime_type or ""
    ).lower()

    if mime_type in ALLOWED_IMAGE_TYPES:
        return "image"

    if mime_type in ALLOWED_PDF_TYPES:
        return "pdf"

    if mime_type in ALLOWED_VIDEO_TYPES:
        return "video"

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail=(
            "Unsupported file type. "
            "Use PNG, JPG, WEBP, PDF, MP4, WEBM or MOV."
        ),
    )


@router.get(
    "/{trade_id}/attachments",
    response_model=TradeAttachmentListResponse,
)
def list_trade_attachments(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    get_owned_trade(
        db,
        current_user.id,
        trade_id,
    )

    attachments = (
        db.query(TradeAttachment)
        .filter(
            TradeAttachment.trade_id == trade_id,
            TradeAttachment.user_id == current_user.id,
        )
        .order_by(
            TradeAttachment.created_at.desc()
        )
        .all()
    )

    return {
        "total": len(attachments),
        "attachments": attachments,
    }


@router.post(
    "/{trade_id}/attachments",
    response_model=TradeAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_trade_attachment(
    trade_id: int,
    file: UploadFile = File(...),
    stage: str = Form("general"),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    get_owned_trade(
        db,
        current_user.id,
        trade_id,
    )

    attachment_type = (
        detect_attachment_type(
            file.content_type
        )
    )

    valid_stages = {
        "general",
        "before",
        "after",
        "strategy",
    }

    stage = (
        stage
        .strip()
        .lower()
    )

    if stage not in valid_stages:
        raise HTTPException(
            status_code=422,
            detail=(
                "Stage must be general, "
                "before, after or strategy."
            ),
        )

    contents = await file.read()

    if attachment_type == "video":
        max_size = (
            50 * 1024 * 1024
        )
    else:
        max_size = (
            15 * 1024 * 1024
        )

    if len(contents) > max_size:
        raise HTTPException(
            status_code=413,
            detail=(
                "Video exceeds 50 MB."
                if attachment_type == "video"
                else "File exceeds 15 MB."
            ),
        )

    original_name = (
        file.filename
        or "attachment"
    )

    extension = (
        Path(original_name)
        .suffix
        .lower()
    )

    stored_name = (
        f"{uuid4().hex}{extension}"
    )

    user_directory = (
        UPLOAD_ROOT /
        str(current_user.id) /
        str(trade_id)
    )

    user_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        user_directory /
        stored_name
    )

    destination.write_bytes(
        contents
    )

    attachment = TradeAttachment(
        user_id=current_user.id,
        trade_id=trade_id,
        attachment_type=attachment_type,
        stage=stage,
        original_name=original_name,
        stored_name=stored_name,
        mime_type=file.content_type,
        file_path=str(destination),
        file_size=len(contents),
    )

    db.add(
        attachment
    )

    db.commit()
    db.refresh(
        attachment
    )

    return attachment


@router.get(
    "/{trade_id}/attachments/{attachment_id}/file",
)
def get_trade_attachment_file(
    trade_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    attachment = (
        get_owned_attachment(
            db,
            current_user.id,
            trade_id,
            attachment_id,
        )
    )

    path = Path(
        attachment.file_path
    )

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Attachment file not found.",
        )

    return FileResponse(
        path=str(path),
        media_type=attachment.mime_type,
        filename=attachment.original_name,
    )


@router.delete(
    "/{trade_id}/attachments/{attachment_id}",
)
def delete_trade_attachment(
    trade_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    attachment = (
        get_owned_attachment(
            db,
            current_user.id,
            trade_id,
            attachment_id,
        )
    )

    path = Path(
        attachment.file_path
    )

    db.delete(
        attachment
    )

    db.commit()

    if path.exists():
        try:
            path.unlink()
        except OSError:
            pass

    return {
        "success": True,
        "message": "Attachment deleted.",
    }
