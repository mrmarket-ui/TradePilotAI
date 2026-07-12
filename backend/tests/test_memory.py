from pprint import pprint

from services.ai_chat.memory import (
    add_message,
    get_history,
    clear_history,
)

clear_history(1)

add_message(
    1,
    "user",
    "Hello"
)

add_message(
    1,
    "assistant",
    "Hi trader."
)

pprint(
    get_history(1)
)
