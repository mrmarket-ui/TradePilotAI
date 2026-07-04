def psychology_analysis(trade):

    if not trade.emotion:
        return "No emotion recorded."

    emotion = trade.emotion.lower()

    messages = {
        "fear": "Fear often causes early exits.",
        "greed": "Greed usually results in holding too long.",
        "revenge": "Revenge trading is one of the fastest ways to lose consistency.",
        "panic": "Panic leads to emotional decisions.",
        "calm": "Excellent emotional control.",
        "patient": "Patience is a professional trader's advantage.",
        "confident": "Healthy confidence improves execution."
    }

    return messages.get(
        emotion,
        "Emotion recorded successfully."
    )