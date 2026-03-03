import ast
from pathlib import Path


class CodeAnalyzer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.report = []

    def analyze(self):
        for file in self.root_path.rglob("*.py"):
            self._analyze_file(file)

        return self.report

    def _analyze_file(self, file_path: Path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return

        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        for func in functions:
            line_count = func.end_lineno - func.lineno if func.end_lineno else 0

            if line_count > 30:
                self.report.append(
                    f"{file_path.name}: Function '{func.name}' is too large ({line_count} lines)"
                )

        imports = [node for node in ast.walk(tree) if isinstance(node, ast.Import)]

        if len(imports) > 10:
            self.report.append(
                f"{file_path.name}: Too many imports ({len(imports)})"
            )