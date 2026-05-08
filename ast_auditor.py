"""Static AST analyzer to detect unsafe calls or unfinished placeholders in AI code."""
import ast
from typing import List

BANNED_CALLS = {"eval", "exec"}
BANNED_IMPORTS = {"pickle"}

class CodeQualityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.warnings: List[str] = []

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in BANNED_CALLS:
            self.warnings.append(f"Line {node.lineno}: Unsafe call to '{node.func.id}()'")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name.split(".")[0] in BANNED_IMPORTS:
                self.warnings.append(f"Line {node.lineno}: Unsafe import '{alias.name}'")
        self.generic_visit(node)

    def visit_Pass(self, node: ast.Pass):
        self.warnings.append(f"Line {node.lineno}: Unimplemented 'pass' placeholder detected")
        self.generic_visit(node)

def audit_python_ast(code_str: str) -> List[str]:
    try:
        tree = ast.parse(code_str)
    except SyntaxError as exc:
        return [f"SyntaxError at line {exc.lineno}: {exc.msg}"]
    visitor = CodeQualityVisitor()
    visitor.visit(tree)
    return visitor.warnings
