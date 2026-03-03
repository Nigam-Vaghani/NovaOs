from novaos.utils.logger import setup_logger
setup_logger()

def interpret(text: str) -> dict:
    """
    Converts natural language to structured command.
    """

    text = text.lower()

    if "system" in text:
        return {"action": "check_system"}

    if "hello" in text:
        return {"action": "greet"}
    
    if "organize" in text:
        return {
            "action": "organize_directory",
            "target": "downloads",
            "mode": "by_extension",
            "dry_run": True
        }

    return {"action": "unknown", "original": text}