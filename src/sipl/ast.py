from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True, slots=True)
class SourceSpan:
    line: int
    column: int
    end_line: int
    end_column: int
    start_pos: int
    end_pos: int

    def to_dict(self) -> dict[str, int]:
        return {
            "line": self.line,
            "column": self.column,
            "end_line": self.end_line,
            "end_column": self.end_column,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
        }


@dataclass(frozen=True, slots=True)
class Number:
    value: int
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class Variable:
    name: str
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class BinaryArithmetic:
    operator: str
    left: Arithmetic
    right: Arithmetic
    span: SourceSpan


Arithmetic: TypeAlias = Number | Variable | BinaryArithmetic


@dataclass(frozen=True, slots=True)
class Comparison:
    operator: str
    left: Arithmetic
    right: Arithmetic
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class LogicalOr:
    left: Boolean
    right: Boolean
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class LogicalNot:
    operand: Boolean
    span: SourceSpan


Boolean: TypeAlias = Comparison | LogicalOr | LogicalNot


@dataclass(frozen=True, slots=True)
class Assignment:
    name: str
    expression: Arithmetic
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class Sequence:
    statements: tuple[Statement, ...]
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class If:
    condition: Boolean
    then_branch: Statement
    else_branch: Statement
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class While:
    condition: Boolean
    body: Statement
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class Block:
    statement: Statement
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class Skip:
    span: SourceSpan


Statement: TypeAlias = Assignment | Sequence | If | While | Block | Skip


@dataclass(frozen=True, slots=True)
class Program:
    statement: Statement
    span: SourceSpan
