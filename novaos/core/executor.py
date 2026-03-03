import psutil
import os
import shutil
from pathlib import Path
import json
from novaos.intelligence.code_analyzer import CodeAnalyzer

UNDO_FILE = Path.home() / ".novaos" / "novaos_undo.json"


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
            UNDO_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(UNDO_FILE, "w") as f:
                json.dump(undo_log, f, indent=4)

        if not moved_files:
            if dry_run:
                return ["No files to organize in Downloads."]
            return ["No files were moved, so undo data was not created."]

        return moved_files

    # -----------------------------
    # UNKNOWN COMMAND
    # -----------------------------
        # -----------------------------
    # UNDO LAST ORGANIZATION
    # -----------------------------
        # -----------------------------
    # PROJECT ANALYSIS
    # -----------------------------
    if action == "analyze_project":
        root = Path.cwd()
        analyzer = CodeAnalyzer(root)
        report = analyzer.analyze()

        if not report:
            return "No major issues found."

        return report
    
    if action == "undo_last":
        undo_file = UNDO_FILE

        if not undo_file.exists():
            return "No undo data found. Run `nova command \"organize downloads\" --force` first."

        # import json

        with open(undo_file, "r") as f:
            undo_log = json.load(f)

        restored = []
        affected_folders = set()

        for entry in undo_log:
            original = Path(entry["original"])
            restore_to = Path(entry["restore_to"])

            if original.exists():
                shutil.move(str(original), str(restore_to))
                restored.append(f"Restored {restore_to.name}")
                affected_folders.add(original.parent)

        # Remove empty folders
        for folder in affected_folders:
            try:
                if folder.exists() and not any(folder.iterdir()):
                    folder.rmdir()
                    restored.append(f"Removed empty folder {folder.name}")
            except Exception:
                pass

        undo_file.unlink()

        if not restored:
            return ["Nothing to restore from the last operation."]

        return restored
    return "Unknown command"