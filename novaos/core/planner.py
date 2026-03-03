def create_plan(command: dict):
    action = command.get("action")

    # Single-step actions
    if action in [
        "check_system",
        "greet",
        "organize_directory",
        "undo_last",
        "analyze_project",
        "fix_unused_imports",
    ]:
        return [command]

    # Multi-step example
    if action == "analyze_and_fix":
        return [
            {"action": "analyze_project"},
            {"action": "fix_unused_imports", "dry_run": False},
            {"action": "analyze_project"},
        ]

    return [command]