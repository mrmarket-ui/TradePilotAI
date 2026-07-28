from fastapi import (
    APIRouter,
    Depends,
)

from dependencies.subscription import (
    require_premium_plan,
)
from models.user import User

from services.ai_engine.signal_generator import (
    SignalGenerator,
)


router = APIRouter()


@router.get("/signals")
def get_signal(
    current_user: User = Depends(
        require_premium_plan,
    ),
):
    market_data = {}

    return SignalGenerator.generate(
        market_data,
    )
