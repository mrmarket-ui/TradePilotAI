from fastapi import APIRouter

from services.ai_engine.signal_generator import SignalGenerator

router = APIRouter()


@router.get("/signals")
def get_signal():

    market_data = {}

    return SignalGenerator.generate(
        market_data
    )