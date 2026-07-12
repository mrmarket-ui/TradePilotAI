"""
TradePilot AI
Conversation Memory
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List


MAX_HISTORY = 20

_MEMORY: Dict[int, List[dict]] = defaultdict(list)


def get_history(user_id: int) -> list[dict]:
    return list(_MEMORY[user_id])


def add_message(
    user_id: int,
    role: str,
    content: str,
) -> None:

    history = _MEMORY[user_id]

    history.append(
        {
            "role": role,
            "content": content,
        }
    )

    if len(history) > MAX_HISTORY:
        del history[:-MAX_HISTORY]


def clear_history(
    user_id: int,
) -> None:

    _MEMORY[user_id].clear()
