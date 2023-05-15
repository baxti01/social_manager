from typing import List


def format_chats(chats: List) -> List[tuple[str, str]]:
    choices = []
    for chat in chats:
        key = chat['id']
        value = f"{chat['name']}: {chat['account_type']}"
        choices.append((str(key), str(value)))

    return choices
