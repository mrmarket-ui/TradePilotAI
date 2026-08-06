from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.auth import get_current_user
from models.strategy_source import StrategySource
from models.user import User
from schemas.strategy_profile import StrategyProfileCreate
from services.strategy_lab.crud import create_strategy
from services.strategy_lab.validator import validate_strategy_create

from schemas.strategy_source import (
    StrategyExtractionResponse,
    StrategySourceResponse,
    StrategyUrlCreate,
)
from services.strategy_ingestion.video import (
    transcribe_video,
)

from services.strategy_ingestion.extractor import (
    extract_pdf_text,
    extract_strategy,
    extract_strategy_from_image,
    extract_text_file,
    fetch_url_text,
)


router = APIRouter(
    prefix="/strategy-sources",
    tags=["Strategy Sources"],
)


UPLOAD_ROOT = Path(
    "storage/strategy_sources"
)

UPLOAD_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".mp4",
    ".mov",
    ".m4v",
}


@router.get(
    "",
    response_model=list[
        StrategySourceResponse
    ],
)
def list_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    return (
        db.query(StrategySource)
        .filter(
            StrategySource.user_id
            == current_user.id
        )
        .order_by(
            StrategySource.created_at.desc()
        )
        .all()
    )


@router.post(
    "/upload",
    response_model=StrategySourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_source(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    name = file.filename or "strategy"

    extension = Path(
        name
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type.",
        )

    source_type = {
        ".pdf": "pdf",
        ".txt": "text",
        ".md": "text",
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
        ".webp": "image",
        ".mp4": "video",
        ".mov": "video",
        ".m4v": "video",
    }.get(
        extension,
        "file",
    )

    contents = await file.read()

    if source_type == "video":
        max_size = 150 * 1024 * 1024
        size_message = "Video exceeds 150 MB."
    else:
        max_size = 50 * 1024 * 1024
        size_message = "File exceeds 50 MB."

    if len(contents) > max_size:
        raise HTTPException(
            status_code=413,
            detail=size_message,
        )

    user_dir = (
        UPLOAD_ROOT /
        str(current_user.id)
    )

    user_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_name = (
        f"{uuid4().hex}{extension}"
    )

    destination = (
        user_dir /
        stored_name
    )

    destination.write_bytes(
        contents
    )

    source = StrategySource(
        user_id=current_user.id,
        source_type=source_type,
        original_name=name,
        mime_type=file.content_type,
        file_path=str(destination),
        status="uploaded",
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source

@router.post(
    "/url",
    response_model=StrategySourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_url_source(
    payload: StrategyUrlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    source = StrategySource(
        user_id=current_user.id,
        source_type="url",
        source_url=str(payload.url),
        status="uploaded",
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


@router.post(
    "/{source_id}/analyze",
    response_model=StrategyExtractionResponse,
)
def analyze_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    source = (
        db.query(StrategySource)
        .filter(
            StrategySource.id
            == source_id,
            StrategySource.user_id
            == current_user.id,
        )
        .first()
    )

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Strategy source not found.",
        )

    try:
        if source.source_type == "pdf":
            text = extract_pdf_text(
                source.file_path,
            )

        elif source.source_type == "text":
            text = extract_text_file(
                source.file_path,
            )

        elif source.source_type == "url":
            text = fetch_url_text(
                source.source_url,
            )

        elif source.source_type == "image":
            strategy = extract_strategy_from_image(
                source.file_path,
            )

            text = (
                "Strategy extracted from image."
            )

        elif source.source_type == "video":
            text = transcribe_video(
                source.file_path,
            )

        else:
            raise ValueError(
                "Unsupported source."
            )

        if source.source_type != "image":
            strategy = extract_strategy(
                text
            )

        source.extracted_text = text
        source.extracted_strategy = strategy
        source.status = "analyzed"
        source.analyzed_at = datetime.utcnow()
        source.error_message = None

        db.commit()

        return {
            "source_id": source.id,
            "status": source.status,
            "strategy": strategy,
        }

    except HTTPException:
        raise

    except Exception as exc:
        source.status = "failed"
        source.error_message = str(exc)

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=(
                "Strategy analysis failed."
            ),
        ) from exc



@router.post(
    "/{source_id}/save-strategy",
)
def save_source_as_strategy(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    source = (
        db.query(StrategySource)
        .filter(
            StrategySource.id == source_id,
            StrategySource.user_id
            == current_user.id,
        )
        .first()
    )

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Strategy source not found.",
        )

    if not source.extracted_strategy:
        raise HTTPException(
            status_code=400,
            detail=(
                "Analyze the source before "
                "saving it as a strategy."
            ),
        )

    raw = dict(
        source.extracted_strategy
    )

    allowed = (
        StrategyProfileCreate
        .model_fields
        .keys()
    )

    payload_data = {
        key: value
        for key, value in raw.items()
        if (
            key in allowed
            and value is not None
        )
    }

    if not payload_data.get("name"):
        payload_data["name"] = (
            source.original_name
            or "AI Imported Strategy"
        )[:120]

    payload = StrategyProfileCreate(
        **payload_data
    )

    try:
        validate_strategy_create(
            payload
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    strategy = create_strategy(
        db=db,
        user_id=current_user.id,
        payload=payload,
    )

    return {
        "success": True,
        "source_id": source.id,
        "strategy_id": strategy.id,
        "name": strategy.name,
    }



