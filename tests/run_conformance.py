import json
from pathlib import Path

from sipl.interpreter import execute
from sipl.parser import SIPLSyntaxError, ast_to_dict, parse


def main() -> int:
    data = json.loads((Path(__file__).parent / "conformance.json").read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        try:
            program = parse(case["source"])
            if not case["valid"]:
                failures.append(f"{case['id']}: expected syntax error")
                continue
            if ast_to_dict(program) != case["expected_ast"]:
                failures.append(f"{case['id']}: AST does not match expected structure")
                continue
            if case.get("execution"):
                state = execute(program, case.get("initial_state", {})).state
                if state != case["expected_state"]:
                    failures.append(f"{case['id']}: expected state {case['expected_state']}, got {state}")
        except SIPLSyntaxError:
            if case["valid"]:
                failures.append(f"{case['id']}: unexpected syntax error")
    if failures:
        print("\n".join(failures))
        return 1
    print(f"Conformance passed: {len(data['cases'])} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
