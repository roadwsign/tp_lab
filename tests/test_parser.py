import pytest

from sipl import ast
from sipl.parser import SIPLSyntaxError, parse, parse_tree

POSITIVE = [
    "begin skip end",
    "begin X := 1 end",
    "begin X := X + 1 end",
    "begin X := X - 1 end",
    "begin X := X * 2 end",
    "begin X := (X + 1) * 2 end",
    "begin X := 1; Y := 2 end",
    "begin if X = 0 then skip else X := 1 end",
    "begin while X > 0 do X := X - 1 end",
    "begin begin X := 1; Y := 2 end end",
    "begin if ¬(X = 0) then X := 1 else X := 0 end",
    "begin if X > 0 ∨ Y > 0 then skip else skip end",
]

NEGATIVE = [
    "skip",
    "begin X = 1 end",
    "begin X := end",
    "begin X := 1;",
    "begin if X > 0 then skip end",
    "begin while X > 0 X := 1 end",
    "begin X := (1 + 2 end",
    "begin X := 1; end",
    "begin begin skip end",
    "begin X := 1 Y := 2 end",
    "begin if X > 0 then skip else end",
    "begin X := 01 end",
]


@pytest.mark.parametrize("source", POSITIVE)
def test_positive_programs(source):
    assert isinstance(parse(source), ast.Program)


@pytest.mark.parametrize("source", NEGATIVE)
def test_negative_programs(source):
    with pytest.raises(SIPLSyntaxError):
        parse(source)


def test_source_span_is_preserved():
    program = parse("begin X := 12 end")
    assert program.statement.span.line == 1
    assert program.statement.span.column == 7


def test_parse_tree_is_available():
    assert parse_tree("begin skip end").data == "start"


def test_arithmetic_precedence():
    program = parse("begin X := 1 + 2 * 3 end")
    expression = program.statement.expression
    assert isinstance(expression, ast.BinaryArithmetic)
    assert expression.operator == "+"
    assert isinstance(expression.right, ast.BinaryArithmetic)
    assert expression.right.operator == "*"


def test_sequence_has_two_statements():
    program = parse("begin X := 1; Y := 2 end")
    assert isinstance(program.statement, ast.Sequence)
    assert len(program.statement.statements) == 2
