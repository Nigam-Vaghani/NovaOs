import psutil
import os
import shutil
from pathlib import Path
import json


def execute(command: dict):
    action = command.get("action")

    # -----------------------------
    # SYSTEM MONITORING
    # -----------------------------
    if action == "check_system":
        return {
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
        }

    # -----------------------------
    # GREETING
    # -----------------------------
    if action == "greet":
        return "Hello from NovaOS 🚀"

    # -----------------------------
    # DIRECTORY ORGANIZER
    # -----------------------------
    if action == "organize_directory":
        target = command.get("target")
        dry_run = command.get("dry_run", True)

        if target == "downloads":
            directory = Path.home() / "Downloads"
        else:
            return "Unknown directory target"

        if not directory.exists():
            return "Directory not found"

        moved_files = []
        undo_log = []

        for file in directory.iterdir():
            if file.is_file():
                extension = file.suffix[1:] or "no_extension"
                new_folder = directory / extension
                new_path = new_folder / file.name

                if dry_run:
                    moved_files.append(
                        f"[DRY RUN] Would move {file.name} → {extension}/"
                    )
                else:
                    new_folder.mkdir(exist_ok=True)
                    shutil.move(str(file), str(new_path))
                    moved_files.append(
                        f"Moved {file.name} → {extension}/"
                    )

                    undo_log.append({
                        "original": str(new_path),
                        "restore_to": str(directory / file.name)
                    })

        # Save undo log if real execution
        if not dry_run and undo_log:
            with open("novaos_undo.json", "w") as f:
                json.dump(undo_log, f, indent=4)

        return moved_files

    # -----------------------------
    # UNKNOWN COMMAND
    # -----------------------------
    return "Unknown command"