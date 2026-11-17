import json
from pathlib import Path

import pytest

from sipl.parser import SIPLSyntaxError, ast_to_dict, parse

DATA = json.loads((Path(__file__).parent / "conformance.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", DATA["cases"], ids=lambda case: case["id"])
def test_conformance_cases(case):
    if case["valid"]:
        program = parse(case["source"])
        assert ast_to_dict(program) == case["expected_ast"]
    else:
        with pytest.raises(SIPLSyntaxError):
            parse(case["source"])
