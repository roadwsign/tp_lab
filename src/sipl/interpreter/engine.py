from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sipl import ast


class SIPLRuntimeError(Exception):
    pass


class StepLimitExceeded(SIPLRuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class TraceEvent:
    event: str
    step: int
    statement: str | None
    span: dict[str, int] | None
    state: dict[str, int]
    variable: str | None = None
    old_value: int | None = None
    new_value: int | None = None
    condition: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "step": self.step,
            "statement": self.statement,
            "span": self.span,
            "state": dict(self.state),
            "variable": self.variable,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "condition": self.condition,
        }


@dataclass(slots=True)
class ExecutionResult:
    state: dict[str, int]
    steps: int
    trace: list[TraceEvent]

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": dict(self.state),
            "steps": self.steps,
            "trace": [event.to_dict() for event in self.trace],
        }


class Interpreter:
    def __init__(self, max_steps: int = 100_000, trace: bool = False):
        if max_steps < 1:
            raise ValueError("max_steps must be greater than zero")
        self.max_steps = max_steps
        self.collect_trace = trace
        self.state: dict[str, int] = {}
        self.events: list[TraceEvent] = []
        self.steps = 0

    def run(self, program: ast.Program, initial_state: dict[str, int] | None = None) -> ExecutionResult:
        self.state = dict(initial_state or {})
        self.events = []
        self.steps = 0
        self._execute(program.statement)
        self._emit("ProgramTerminated", None, None)
        return ExecutionResult(dict(self.state), self.steps, list(self.events))

    def _emit(
        self,
        event: str,
        statement: ast.Statement | None,
        statement_name: str | None,
        variable: str | None = None,
        old_value: int | None = None,
        new_value: int | None = None,
        condition: bool | None = None,
    ) -> None:
        if self.collect_trace:
            span = statement.span.to_dict() if statement is not None else None
            self.events.append(
                TraceEvent(
                    event=event,
                    step=self.steps,
                    statement=statement_name,
                    span=span,
                    state=dict(self.state),
                    variable=variable,
                    old_value=old_value,
                    new_value=new_value,
                    condition=condition,
                )
            )

    def _tick(self, statement: ast.Statement) -> None:
        self.steps += 1
        if self.steps > self.max_steps:
            raise StepLimitExceeded(f"Execution exceeded the limit of {self.max_steps} steps")
        self._emit("BeforeStatement", statement, type(statement).__name__)

    def _execute(self, statement: ast.Statement) -> None:
        self._tick(statement)
        if isinstance(statement, ast.Assignment):
            value = self._arithmetic(statement.expression)
            old = self.state.get(statement.name)
            self.state[statement.name] = value
            self._emit("VariableChanged", statement, "Assignment", statement.name, old, value)
        elif isinstance(statement, ast.Sequence):
            for child in statement.statements:
                self._execute(child)
        elif isinstance(statement, ast.If):
            result = self._boolean(statement.condition)
            self._emit("ConditionChecked", statement, "If", condition=result)
            self._execute(statement.then_branch if result else statement.else_branch)
        elif isinstance(statement, ast.While):
            while True:
                result = self._boolean(statement.condition)
                self._emit("ConditionChecked", statement, "While", condition=result)
                if not result:
                    break
                self._execute(statement.body)
        elif isinstance(statement, ast.Block):
            self._execute(statement.statement)
        elif isinstance(statement, ast.Skip):
            pass
        else:
            raise SIPLRuntimeError(f"Unsupported statement: {type(statement).__name__}")
        self._emit("AfterStatement", statement, type(statement).__name__)

    def _arithmetic(self, expression: ast.Arithmetic) -> int:
        if isinstance(expression, ast.Number):
            return expression.value
        if isinstance(expression, ast.Variable):
            if expression.name not in self.state:
                raise SIPLRuntimeError(f"Variable {expression.name!r} is not defined")
            return self.state[expression.name]
        if isinstance(expression, ast.BinaryArithmetic):
            left = self._arithmetic(expression.left)
            right = self._arithmetic(expression.right)
            if expression.operator == "+":
                return left + right
            if expression.operator == "-":
                return left - right
            if expression.operator == "*":
                return left * right
        raise SIPLRuntimeError(f"Unsupported arithmetic expression: {type(expression).__name__}")

    def _boolean(self, expression: ast.Boolean) -> bool:
        if isinstance(expression, ast.Comparison):
            left = self._arithmetic(expression.left)
            right = self._arithmetic(expression.right)
            return left == right if expression.operator == "=" else left > right
        if isinstance(expression, ast.LogicalOr):
            return self._boolean(expression.left) or self._boolean(expression.right)
        if isinstance(expression, ast.LogicalNot):
            return not self._boolean(expression.operand)
        raise SIPLRuntimeError(f"Unsupported boolean expression: {type(expression).__name__}")


def execute(
    program: ast.Program,
    initial_state: dict[str, int] | None = None,
    max_steps: int = 100_000,
    trace: bool = False,
) -> ExecutionResult:
    return Interpreter(max_steps=max_steps, trace=trace).run(program, initial_state)
