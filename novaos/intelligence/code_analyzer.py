import ast
from pathlib import Path


class CodeAnalyzer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.report = []

    def analyze(self):
        for file in self.root_path.rglob("*.py"):
            self._analyze_file(file)

        if not self.report:
            return {"status": "clean", "issues": []}

        return {"status": "issues_found", "issues": self.report}

    def _analyze_file(self, file_path: Path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except Exception:
            return

        self._check_large_functions(tree, file_path)
        self._check_unused_imports(tree, file_path)
        self._check_complexity(tree, file_path)

    # ----------------------------------
    # LARGE FUNCTION CHECK
    # ----------------------------------
    def _check_large_functions(self, tree, file_path):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, "end_lineno") and node.end_lineno:
                    line_count = node.end_lineno - node.lineno
                    if line_count > 40:
                        self.report.append({
                            "file": file_path.name,
                            "type": "large_function",
                            "function": node.name,
                            "lines": line_count
                        })

    # ----------------------------------
    # UNUSED IMPORT CHECK
    # ----------------------------------
    def _check_unused_imports(self, tree, file_path):
        imports = []
        used_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split(".")[0])

            if isinstance(node, ast.Name):
                used_names.add(node.id)

        for imp in imports:
            if imp not in used_names:
                self.report.append({
                    "file": file_path.name,
                    "type": "unused_import",
                    "import": imp
                })

    # ----------------------------------
    # COMPLEXITY CHECK (Simple Heuristic)
    # ----------------------------------
    def _check_complexity(self, tree, file_path):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = 0

                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                        complexity += 1

                if complexity > 10:
                    self.report.append({
                        "file": file_path.name,
                        "type": "high_complexity",
                        "function": node.name,
                        "complexity_score": complexity
                    })