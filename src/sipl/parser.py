from __future__ import annotations

from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any

from lark import Lark, Token, Transformer, UnexpectedInput, v_args
from lark.tree import Meta, Tree

from sipl import ast

GRAMMAR_PATH = Path(__file__).resolve().parent / "grammar" / "sipl.lark"


class SIPLSyntaxError(Exception):
    def __init__(self, message: str, line: int, column: int, expected: list[str] | None = None):
        self.message = message
        self.line = line
        self.column = column
        self.expected = expected or []
        super().__init__(f"{message} at line {line}, column {column}")


def _span(meta: Meta) -> ast.SourceSpan:
    return ast.SourceSpan(
        line=getattr(meta, "line", 1) or 1,
        column=getattr(meta, "column", 1) or 1,
        end_line=getattr(meta, "end_line", 1) or 1,
        end_column=getattr(meta, "end_column", 1) or 1,
        start_pos=getattr(meta, "start_pos", 0) or 0,
        end_pos=getattr(meta, "end_pos", 0) or 0,
    )


@v_args(meta=True)
class ASTBuilder(Transformer):
    def start(self, meta: Meta, children: list[Any]) -> ast.Program:
        return ast.Program(children[0], _span(meta))

    def number(self, meta: Meta, children: list[Token]) -> ast.Number:
        return ast.Number(int(children[0]), _span(meta))

    def variable(self, meta: Meta, children: list[Token]) -> ast.Variable:
        return ast.Variable(str(children[0]), _span(meta))

    def add(self, meta: Meta, children: list[Any]) -> ast.BinaryArithmetic:
        return ast.BinaryArithmetic("+", children[0], children[1], _span(meta))

    def subtract(self, meta: Meta, children: list[Any]) -> ast.BinaryArithmetic:
        return ast.BinaryArithmetic("-", children[0], children[1], _span(meta))

    def multiply(self, meta: Meta, children: list[Any]) -> ast.BinaryArithmetic:
        return ast.BinaryArithmetic("*", children[0], children[1], _span(meta))

    def equal(self, meta: Meta, children: list[Any]) -> ast.Comparison:
        return ast.Comparison("=", children[0], children[1], _span(meta))

    def greater(self, meta: Meta, children: list[Any]) -> ast.Comparison:
        return ast.Comparison(">", children[0], children[1], _span(meta))

    def logical_or(self, meta: Meta, children: list[Any]) -> ast.LogicalOr:
        return ast.LogicalOr(children[0], children[1], _span(meta))

    def logical_not(self, meta: Meta, children: list[Any]) -> ast.LogicalNot:
        return ast.LogicalNot(children[0], _span(meta))

    def assignment(self, meta: Meta, children: list[Any]) -> ast.Assignment:
        return ast.Assignment(str(children[0]), children[1], _span(meta))

    def sequence(self, meta: Meta, children: list[Any]) -> ast.Sequence:
        return ast.Sequence(tuple(children), _span(meta))

    def if_statement(self, meta: Meta, children: list[Any]) -> ast.If:
        return ast.If(children[0], children[1], children[2], _span(meta))

    def while_statement(self, meta: Meta, children: list[Any]) -> ast.While:
        return ast.While(children[0], children[1], _span(meta))

    def block(self, meta: Meta, children: list[Any]) -> ast.Block:
        return ast.Block(children[0], _span(meta))

    def skip_statement(self, meta: Meta, children: list[Any]) -> ast.Skip:
        return ast.Skip(_span(meta))


_parser = Lark.open(str(GRAMMAR_PATH), parser="lalr", start="start", propagate_positions=True)


def parse(source: str) -> ast.Program:
    try:
        tree = _parser.parse(source)
        return ASTBuilder().transform(tree)
    except UnexpectedInput as error:
        expected = sorted(getattr(error, "expected", []) or [])
        token = getattr(error, "token", None)
        if token is not None and str(token) and str(token) != "$END":
            message = f"Unexpected token {str(token)!r}"
        else:
            message = "Unexpected end of input"
        raise SIPLSyntaxError(message, error.line, error.column, expected) from None


def parse_tree(source: str) -> Tree:
    try:
        return _parser.parse(source)
    except UnexpectedInput as error:
        expected = sorted(getattr(error, "expected", []) or [])
        token = getattr(error, "token", None)
        message = f"Unexpected token {str(token)!r}" if token is not None and str(token) and str(token) != "$END" else "Unexpected end of input"
        raise SIPLSyntaxError(message, error.line, error.column, expected) from None


def ast_to_dict(node: Any, source: str | None = None) -> dict[str, Any]:
    if not is_dataclass(node):
        raise TypeError(f"Unsupported AST value: {type(node).__name__}")
    result: dict[str, Any] = {"type": type(node).__name__}
    for item in fields(node):
        value = getattr(node, item.name)
        if isinstance(value, ast.SourceSpan):
            result[item.name] = value.to_dict()
        elif is_dataclass(value):
            result[item.name] = ast_to_dict(value, source)
        elif isinstance(value, tuple):
            result[item.name] = [ast_to_dict(child, source) for child in value]
        else:
            result[item.name] = value.to_dict() if isinstance(value, ast.SourceSpan) else value
    if source is not None and hasattr(node, "span"):
        result["source_fragment"] = source[node.span.start_pos:node.span.end_pos]
    return result
