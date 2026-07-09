from services.consistency.sessions import analyze_sessions
from services.consistency.weekdays import analyze_weekdays
from services.consistency.symbols import analyze_symbols
from services.consistency.strategies import analyze_strategies
from services.consistency.improvements import (
    analyze_monthly_progress,
    improvement_trend,
)
from services.consistency.score import (
    calculate_consistency_score,
)


def analyze_consistency(

    trades,
    statistics,
    risk,
    psychology,
    behavior,

):

    session_analysis = analyze_sessions(trades)

    weekday_analysis = analyze_weekdays(trades)

    symbol_analysis = analyze_symbols(trades)

    strategy_analysis = analyze_strategies(trades)

    monthly_analysis = analyze_monthly_progress(trades)

    trend = improvement_trend(trades)

    score = calculate_consistency_score(

        statistics=statistics,

        risk=risk,

        psychology=psychology,

        behavior=behavior,

        improvement=trend,

    )

    return {

        "score": score,

        "trend": trend,

        "sessions": session_analysis,

        "weekdays": weekday_analysis,

        "symbols": symbol_analysis,

        "strategies": strategy_analysis,

        "monthly_progress": monthly_analysis,

    }
