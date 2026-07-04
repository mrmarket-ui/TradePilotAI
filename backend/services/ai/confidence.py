def confidence_level(score):

    if score >= 90:
        return "Very High"

    if score >= 80:
        return "High"

    if score >= 70:
        return "Medium"

    if score >= 60:
        return "Low"

    return "Very Low"