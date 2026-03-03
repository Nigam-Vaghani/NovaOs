def interpret(text: str) -> dict:
    """
    Converts natural language to structured command.
    """

    text = text.lower()

    if "system" in text:
        return {"action": "check_system"}

    if "hello" in text:
        return {"action": "greet"}

    return {"action": "unknown", "original": text}