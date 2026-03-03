BLACKLISTED_ACTIONS = [
    "delete_root",
    "format_disk",
]

def is_safe(command: dict) -> bool:
    action = command.get("action")
    return action not in BLACKLISTED_ACTIONS