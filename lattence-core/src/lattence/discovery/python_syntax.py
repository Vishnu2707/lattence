import ast
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


class PythonSyntaxError(ValueError):
    pass


@dataclass(frozen=True, order=True)
class SyntaxLocation:
    line: int
    column: int


@dataclass(frozen=True)
class ImportRecord:
    module: str
    name: str | None
    alias: str | None
    location: SyntaxLocation


@dataclass(frozen=True)
class CallRecord:
    function: str
    argument_kinds: tuple[str, ...]
    keyword_names: tuple[str, ...]
    location: SyntaxLocation


@dataclass(frozen=True)
class DecoratorRecord:
    target: str
    decorator: str
    location: SyntaxLocation


@dataclass(frozen=True)
class AssignmentRecord:
    target: str
    value_kind: str
    location: SyntaxLocation


@dataclass(frozen=True)
class PythonSyntax:
    path: str
    imports: tuple[ImportRecord, ...]
    calls: tuple[CallRecord, ...]
    decorators: tuple[DecoratorRecord, ...]
    assignments: tuple[AssignmentRecord, ...]


def _location(node: ast.AST) -> SyntaxLocation:
    return SyntaxLocation(
        int(getattr(node, "lineno", 0)), int(getattr(node, "col_offset", 0))
    )


def _expression_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _expression_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return f"{_expression_name(node.func)}()"
    if isinstance(node, ast.Subscript):
        return f"{_expression_name(node.value)}[]"
    if isinstance(node, ast.Constant):
        return f"<{type(node.value).__name__}>"
    if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
        return f"<{type(node).__name__.lower()}>"
    return f"<{type(node).__name__.lower()}>"


def _target_names(node: ast.AST) -> tuple[str, ...]:
    if isinstance(node, (ast.Name, ast.Attribute, ast.Subscript)):
        return (_expression_name(node),)
    if isinstance(node, (ast.Tuple, ast.List)):
        return tuple(name for item in node.elts for name in _target_names(item))
    return ()


class _SyntaxVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.imports: list[ImportRecord] = []
        self.calls: list[CallRecord] = []
        self.decorators: list[DecoratorRecord] = []
        self.assignments: list[AssignmentRecord] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(
                ImportRecord(alias.name, None, alias.asname, _location(node))
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        prefix = "." * node.level
        module = f"{prefix}{node.module or ''}"
        for alias in node.names:
            self.imports.append(
                ImportRecord(module, alias.name, alias.asname, _location(node))
            )

    def visit_Call(self, node: ast.Call) -> None:
        self.calls.append(
            CallRecord(
                function=_expression_name(node.func),
                argument_kinds=tuple(_expression_name(arg) for arg in node.args),
                keyword_names=tuple(keyword.arg or "**" for keyword in node.keywords),
                location=_location(node),
            )
        )
        self.generic_visit(node)

    def _record_decorators(self, target: str, decorators: list[ast.expr]) -> None:
        for decorator in decorators:
            self.decorators.append(
                DecoratorRecord(
                    target, _expression_name(decorator), _location(decorator)
                )
            )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_decorators(node.name, node.decorator_list)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_decorators(node.name, node.decorator_list)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._record_decorators(node.name, node.decorator_list)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        value_kind = _expression_name(node.value)
        for target in node.targets:
            for name in _target_names(target):
                self.assignments.append(
                    AssignmentRecord(name, value_kind, _location(target))
                )
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        value_kind = _expression_name(node.value) if node.value else "<none>"
        for name in _target_names(node.target):
            self.assignments.append(
                AssignmentRecord(name, value_kind, _location(node.target))
            )
        self.generic_visit(node)


def parse_python_source(source: str, path: str = "<memory>") -> PythonSyntax:
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as error:
        location = f"{error.lineno or 0}:{error.offset or 0}"
        raise PythonSyntaxError(f"cannot parse {path} at {location}") from error

    visitor = _SyntaxVisitor()
    visitor.visit(tree)
    return PythonSyntax(
        path=path,
        imports=tuple(sorted(visitor.imports, key=lambda item: item.location)),
        calls=tuple(sorted(visitor.calls, key=lambda item: item.location)),
        decorators=tuple(sorted(visitor.decorators, key=lambda item: item.location)),
        assignments=tuple(sorted(visitor.assignments, key=lambda item: item.location)),
    )


def parse_python_file(path: Path, project_root: Path) -> PythonSyntax:
    try:
        relative = path.resolve(strict=True).relative_to(
            project_root.resolve(strict=True)
        )
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as error:
        raise PythonSyntaxError(f"cannot read Python source {path}") from error
    relative_path = PurePosixPath(relative).as_posix()
    return parse_python_source(source, relative_path)
