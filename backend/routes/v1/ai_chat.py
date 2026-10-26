from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.subscription import (
    require_paid_plan,
)
from models.user import User

from schemas.ai_chat.request import (
    AIChatRequest,
)
from schemas.ai_chat.response import (
    AIChatResponse,
)

from services.ai_chat.context import (
    build_chat_context,
)
from services.ai_chat.engine import (
    generate_chat_reply,
)


from services.ai_chat.sufficiency import apply_data_sufficiency


router = APIRouter(
    prefix="/ai/chat",
    tags=["AI Chat Coach"],
)


@router.post(
    "",
    response_model=AIChatResponse,
)
def chat_with_coach(
    payload: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_paid_plan,
    ),
):
    context = build_chat_context(
        db=db,
        user_id=current_user.id,
    )

    context = apply_data_sufficiency(
        context,
        int(context.get("trade_count", 0) or 0),
    )

    return generate_chat_reply(
        user_id=current_user.id,
        message=payload.message,
        context=context,
    )
