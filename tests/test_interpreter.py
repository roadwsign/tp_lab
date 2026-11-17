import pytest

from sipl.interpreter import SIPLRuntimeError, StepLimitExceeded, execute
from sipl.parser import parse


def test_power_example():
    program = parse("""begin
        R := 1;
        while Y > 0 do begin R := R * X; Y := Y - 1 end
    end""")
    result = execute(program, {"X": 5, "Y": 2})
    assert result.state == {"X": 5, "Y": 0, "R": 25}


def test_if_true_branch():
    result = execute(parse("begin if X > 0 then R := 1 else R := 2 end"), {"X": 3})
    assert result.state["R"] == 1


def test_if_false_branch():
    result = execute(parse("begin if X > 0 then R := 1 else R := 2 end"), {"X": 0})
    assert result.state["R"] == 2


def test_skip_keeps_state():
    result = execute(parse("begin skip end"), {"X": 7})
    assert result.state == {"X": 7}


def test_block_and_sequence():
    result = execute(parse("begin begin X := 2; Y := X + 3 end end"))
    assert result.state == {"X": 2, "Y": 5}


def test_boolean_or_and_not():
    result = execute(parse("begin if ¬(X = 0) ∨ Y > 2 then R := 1 else R := 0 end"), {"X": 0, "Y": 3})
    assert result.state["R"] == 1


def test_undefined_variable():
    with pytest.raises(SIPLRuntimeError, match="not defined"):
        execute(parse("begin X := Y + 1 end"))


def test_step_limit():
    with pytest.raises(StepLimitExceeded):
        execute(parse("begin while X > 0 do skip end"), {"X": 1}, max_steps=4)


def test_trace_events():
    result = execute(parse("begin X := 2 end"), trace=True)
    event_names = [event.event for event in result.trace]
    assert "BeforeStatement" in event_names
    assert "VariableChanged" in event_names
    assert "AfterStatement" in event_names
    assert event_names[-1] == "ProgramTerminated"


def test_trace_condition_event():
    result = execute(parse("begin if X > 0 then skip else skip end"), {"X": 1}, trace=True)
    assert any(event.event == "ConditionChecked" and event.condition is True for event in result.trace)


def test_trace_is_empty_when_disabled():
    result = execute(parse("begin skip end"))
    assert result.trace == []
