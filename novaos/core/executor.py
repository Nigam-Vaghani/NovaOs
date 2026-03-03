import psutil
import shutil
import json
import ast
from pathlib import Path
from novaos.intelligence.code_analyzer import CodeAnalyzer

UNDO_FILE = Path.home() / ".novaos" / "novaos_undo.json"


def _is_safe_project_file(file_path: Path) -> bool:
    blocked_parts = {
        "os-env",
        "venv",
        ".venv",
        "site-packages",
        "__pycache__",
        ".git",
    }
    return not any(part in blocked_parts for part in file_path.parts)


def _get_import_log_file() -> Path:
    return Path.cwd() / "import_log.json"


def _undo_organized_downloads() -> list[str] | str:
    undo_file = UNDO_FILE

    if not undo_file.exists():
        return "No download-undo data found."

    with open(undo_file, "r", encoding="utf-8") as f:
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

    for folder in affected_folders:
        try:
            if folder.exists() and not any(folder.iterdir()):
                folder.rmdir()
                restored.append(f"Removed empty folder {folder.name}")
        except Exception:
            pass

    undo_file.unlink()

    if not restored:
        return ["Nothing to restore from the last downloads organization."]

    return restored


def _undo_import_fixes() -> list[str] | str:
    log_file = _get_import_log_file()

    if not log_file.exists():
        return "No import undo data found."

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            log_data = json.load(f)
    except Exception:
        log_file.unlink(missing_ok=True)
        return "import_log.json was invalid and has been removed."

    restored = []

    for file_entry in log_data.get("files", []):
        file_path = Path(file_entry.get("file", ""))
        removed_imports = file_entry.get("removed_imports", [])

        if not file_path.exists():
            restored.append(f"Skipped missing file: {file_path.name}")
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        except Exception:
            restored.append(f"Failed to read: {file_path.name}")
            continue

        offset = 0
        added_count = 0

        for item in sorted(removed_imports, key=lambda x: x.get("line", 1)):
            line_number = max(1, int(item.get("line", 1)))
            import_line = item.get("content", "").rstrip("\n")

            if not import_line:
                continue

            if import_line in lines:
                continue

            insert_at = min(len(lines), line_number - 1 + offset)
            lines.insert(insert_at, import_line)
            offset += 1
            added_count += 1

        if added_count:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            restored.append(f"Restored imports in {file_path.name}")

    log_file.unlink()

    if not restored:
        return ["Nothing to restore from import_log.json."]

    return restored


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

        # Save report to file
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"novaos_report_{timestamp}.json")

        with open(report_file, "w") as f:
            json.dump(report, f, indent=4)

        return {
            "message": f"Report saved to {report_file.name}",
            "summary": report
        }
    
    # -----------------------------
    # FIX UNUSED IMPORTS
    # -----------------------------
    if action == "fix_unused_imports":
        root = Path.cwd()
        source_root = root / "novaos"
        import_log_file = _get_import_log_file()
        dry_run = command.get("dry_run", True)

        changes = []
        import_fix_log = {
            "action": "fix_unused_imports",
            "root": str(root),
            "files": [],
        }

        if not source_root.exists():
            return "Project source folder `novaos` not found."

        for file in source_root.rglob("*.py"):
            if not _is_safe_project_file(file):
                continue

            try:
                with open(file, "r", encoding="utf-8") as f:
                    source = f.read()
                    tree = ast.parse(source)
            except Exception:
                continue

            imports = []
            used_names = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_name = alias.asname or alias.name.split(".")[0]
                        imports.append((imported_name, node.lineno))

                if isinstance(node, ast.ImportFrom):
                    imported_names = [
                        alias.asname or alias.name
                        for alias in node.names
                        if alias.name != "*"
                    ]
                    if imported_names:
                        imports.append((imported_names, node.lineno))

                if isinstance(node, ast.Name):
                    used_names.add(node.id)

            lines = source.splitlines()
            removed_lines = []
            removed_imports_info = []

            for imported, lineno in imports:
                if isinstance(imported, list):
                    is_used = any(name in used_names for name in imported)
                else:
                    is_used = imported in used_names

                if not is_used:
                    line_index = lineno - 1
                    if line_index < 0 or line_index >= len(lines):
                        continue
                    if line_index in removed_lines:
                        continue
                    removed_lines.append(line_index)
                    removed_imports_info.append({
                        "line": lineno,
                        "content": lines[line_index],
                    })

            if removed_lines:
                if dry_run:
                    changes.append(f"[DRY RUN] Would modify {file.name}")
                else:
                    new_lines = [
                        line for idx, line in enumerate(lines)
                        if idx not in removed_lines
                    ]

                    with open(file, "w", encoding="utf-8") as f:
                        f.write("\n".join(new_lines))

                    import_fix_log["files"].append({
                        "file": str(file),
                        "removed_imports": removed_imports_info,
                    })

                    changes.append(f"Modified {file.name}")

        if not changes:
            return "No unused imports found."

        if not dry_run and import_fix_log["files"]:
            with open(import_log_file, "w", encoding="utf-8") as f:
                json.dump(import_fix_log, f, indent=4)
            changes.append(f"Saved undo log: {import_log_file.name}")

        return changes
    
    if action == "undo_last":
        import_log_file = _get_import_log_file()
        has_import_undo = import_log_file.exists()
        has_download_undo = UNDO_FILE.exists()

        if not has_import_undo and not has_download_undo:
            return "No undo data found."

        if has_import_undo and has_download_undo:
            if import_log_file.stat().st_mtime >= UNDO_FILE.stat().st_mtime:
                return _undo_import_fixes()
            return _undo_organized_downloads()

        if has_import_undo:
            return _undo_import_fixes()

        return _undo_organized_downloads()
    return "Unknown command"