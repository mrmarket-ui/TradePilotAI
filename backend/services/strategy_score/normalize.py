import re


ALIASES = {
    "bos": "breakofstructure",
    "break of structure": "breakofstructure",

    "choch": "changeofcharacter",
    "change of character": "changeofcharacter",

    "mss": "marketstructureshift",
    "market structure shift": "marketstructureshift",

    "fvg": "fairvaluegap",
    "fair value gap": "fairvaluegap",

    "htf": "highertimeframealignment",
    "higher timeframe alignment": "highertimeframealignment",
    "higher-timeframe alignment": "highertimeframealignment",

    "pd": "premiumdiscountalignment",
    "premium discount alignment": "premiumdiscountalignment",
    "premium/discount alignment": "premiumdiscountalignment",

    "volume confirmation": "volumeconfirmation",
    "momentum candle": "momentumcandle",

    "liquidity sweep": "liquiditysweep",
    "liquidity taken": "liquiditytaken",
}


def normalize(text: str) -> str:
    if not text:
        return ""

    value = text.lower().strip()

    value = ALIASES.get(value, value)

    value = re.sub(r"[\s\-_\/]+", "", value)

    return value