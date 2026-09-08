import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .python_syntax import SyntaxLocation

_IMPORT = re.compile(
    r"^\s*import\s+(?:(?P<clause>[^;\n]+?)\s+from\s+)?"
    r"(?P<quote>['\"])(?P<module>[^'\"]+)(?P=quote)",
    re.MULTILINE,
)
_REQUIRE = re.compile(
    r"\brequire\s*\(\s*(?P<quote>['\"])(?P<module>[^'\"]+)(?P=quote)\s*\)"
)
_CALL = re.compile(
    r"(?<![\w$])(?P<name>[A-Za-z_$][\w$]*(?:\s*\.\s*[A-Za-z_$][\w$]*)*)\s*\("
)
_NON_CALL_NAMES = frozenset(
    {"catch", "for", "function", "if", "import", "require", "switch", "while"}
)


class JavaScriptSyntaxError(ValueError):
    pass


@dataclass(frozen=True)
class JavaScriptImport:
    module: str
    bindings: tuple[str, ...]
    kind: str
    location: SyntaxLocation


@dataclass(frozen=True)
class JavaScriptCall:
    function: str
    location: SyntaxLocation


@dataclass(frozen=True)
class JavaScriptSyntax:
    path: str
    imports: tuple[JavaScriptImport, ...]
    calls: tuple[JavaScriptCall, ...]


def _mask(source: str, *, strings: bool) -> str:
    output = list(source)
    index = 0
    state = "code"
    quote = ""
    while index < len(source):
        char = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""
        if state == "code" and char == "/" and following == "/":
            output[index] = output[index + 1] = " "
            index += 2
            state = "line_comment"
            continue
        if state == "code" and char == "/" and following == "*":
            output[index] = output[index + 1] = " "
            index += 2
            state = "block_comment"
            continue
        if state == "code" and char in "'\"`":
            quote = char
            if strings:
                output[index] = " "
            index += 1
            state = "string"
            continue
        if state == "line_comment":
            if char == "\n":
                state = "code"
            else:
                output[index] = " "
            index += 1
            continue
        if state == "block_comment":
            if char == "*" and following == "/":
                output[index] = output[index + 1] = " "
                index += 2
                state = "code"
            else:
                if char != "\n":
                    output[index] = " "
                index += 1
            continue
        if state == "string":
            if strings and char != "\n":
                output[index] = " "
            if char == "\\":
                if strings and index + 1 < len(source) and source[index + 1] != "\n":
                    output[index + 1] = " "
                index += 2
                continue
            if char == quote:
                state = "code"
            index += 1
            continue
        index += 1

    if state in {"block_comment", "string"}:
        raise JavaScriptSyntaxError(f"unterminated {state.replace('_', ' ')}")
    return "".join(output)


def _location(source: str, offset: int) -> SyntaxLocation:
    line = source.count("\n", 0, offset) + 1
    previous_newline = source.rfind("\n", 0, offset)
    return SyntaxLocation(line, offset - previous_newline - 1)


def _bindings(clause: str | None) -> tuple[str, ...]:
    if clause is None:
        return ()
    cleaned = clause.strip()
    bindings: list[str] = []
    default, separator, remainder = cleaned.partition(",")
    if default and not default.startswith(("{", "*")):
        bindings.append(default.strip())
        cleaned = remainder if separator else ""
    if "{" in cleaned:
        content = cleaned.partition("{")[2].partition("}")[0]
        bindings.extend(item.strip() for item in content.split(",") if item.strip())
    elif "* as " in cleaned:
        bindings.append(cleaned.split("* as ", 1)[1].strip())
    return tuple(bindings)


def parse_javascript_source(source: str, path: str = "<memory>") -> JavaScriptSyntax:
    comments_masked = _mask(source, strings=False)
    fully_masked = _mask(source, strings=True)
    imports = [
        JavaScriptImport(
            module=match.group("module"),
            bindings=_bindings(match.group("clause")),
            kind="import",
            location=_location(source, match.start()),
        )
        for match in _IMPORT.finditer(comments_masked)
    ]
    imports.extend(
        JavaScriptImport(
            module=match.group("module"),
            bindings=(),
            kind="require",
            location=_location(source, match.start()),
        )
        for match in _REQUIRE.finditer(comments_masked)
    )

    calls: list[JavaScriptCall] = []
    for match in _CALL.finditer(fully_masked):
        function = re.sub(r"\s+", "", match.group("name"))
        if function in _NON_CALL_NAMES:
            continue
        calls.append(JavaScriptCall(function, _location(source, match.start())))

    return JavaScriptSyntax(
        path=path,
        imports=tuple(sorted(imports, key=lambda item: item.location)),
        calls=tuple(calls),
    )


def parse_javascript_file(path: Path, project_root: Path) -> JavaScriptSyntax:
    try:
        relative = path.resolve(strict=True).relative_to(
            project_root.resolve(strict=True)
        )
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as error:
        raise JavaScriptSyntaxError(f"cannot read JavaScript source {path}") from error
    relative_path = PurePosixPath(relative).as_posix()
    return parse_javascript_source(source, relative_path)
