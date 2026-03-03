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
    if "undo import" in text:
        return {"action": "undo_imports"}
    if "undo" in text:
        return {"action": "undo_last"}

    if "analyze" in text:
        return {
            "action": "analyze_project",
            "target": "current_directory"
        }
    if "fix imports" in text or "fix import" in text:
        return {
            "action": "fix_unused_imports",
            "target": "current_directory",
            "dry_run": True
        }
    return {"action": "unknown", "original": text}