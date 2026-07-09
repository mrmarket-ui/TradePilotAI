from services.analytics.risk import (
    calculate_max_drawdown,
    calculate_recovery_factor,
    calculate_expectancy,
)


def analyze_risk(trades):

    return {

        "maximum_drawdown":
            calculate_max_drawdown(trades),

        "recovery_factor":
            calculate_recovery_factor(trades),

        "expectancy":
            calculate_expectancy(trades),

    }
