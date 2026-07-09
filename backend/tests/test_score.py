from services.consistency.score import calculate_consistency_score

statistics = {
    "win_rate": 74,
    "profit_factor": 2.1
}

risk = {
    "recovery_factor": 3.5
}

psychology = {
    "score": 88
}

behavior = {
    "score": 92
}

trend = "Improving"

result = calculate_consistency_score(
    statistics,
    risk,
    psychology,
    behavior,
    trend
)

print(result)
