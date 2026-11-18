import json

from sipl.cli import main


def test_check_command(tmp_path, capsys):
    file = tmp_path / "valid.sipl"
    file.write_text("begin skip end", encoding="utf-8")
    assert main(["check", str(file)]) == 0
    assert "correct" in capsys.readouterr().out


def test_check_json(tmp_path, capsys):
    file = tmp_path / "valid.sipl"
    file.write_text("begin skip end", encoding="utf-8")
    assert main(["check", str(file), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["valid"] is True


def test_parse_json(tmp_path, capsys):
    file = tmp_path / "valid.sipl"
    file.write_text("begin skip end", encoding="utf-8")
    assert main(["parse", str(file), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["type"] == "Program"


def test_parse_comparison_json(tmp_path, capsys):
    file = tmp_path / "valid.sipl"
    file.write_text("begin skip end", encoding="utf-8")
    assert main(["parse", str(file), "--view", "comparison", "--format", "json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert set(result) == {"parse_tree", "ast"}
    assert result["ast"]["type"] == "Program"


def test_parse_tree_dot(tmp_path, capsys):
    file = tmp_path / "valid.sipl"
    file.write_text("begin skip end", encoding="utf-8")
    assert main(["parse", str(file), "--view", "parse-tree", "--format", "dot"]) == 0
    output = capsys.readouterr().out
    assert output.startswith("digraph SIPL {\n")
    assert output.endswith("\n}\n")


def test_parse_ast_svg(tmp_path, capsys):
    file = tmp_path / "valid.sipl"
    file.write_text("begin X := 1 end", encoding="utf-8")
    assert main(["parse", str(file), "--view", "ast", "--format", "svg"]) == 0
    assert "Assignment" in capsys.readouterr().out


def test_parse_comparison_html(tmp_path, capsys):
    file = tmp_path / "valid.sipl"
    file.write_text("begin skip end", encoding="utf-8")
    assert main(["parse", str(file), "--view", "comparison", "--format", "html"]) == 0
    assert "Parse Tree" in capsys.readouterr().out


def test_run_command(tmp_path, capsys):
    file = tmp_path / "valid.sipl"
    file.write_text("begin R := X + 1 end", encoding="utf-8")
    assert main(["run", str(file), "--state", "X=4"]) == 0
    assert json.loads(capsys.readouterr().out)["R"] == 5


def test_trace_command(tmp_path, capsys):
    file = tmp_path / "valid.sipl"
    file.write_text("begin skip end", encoding="utf-8")
    assert main(["trace", str(file)]) == 0
    assert "ProgramTerminated" in capsys.readouterr().out


def test_syntax_error_exit_code(tmp_path, capsys):
    file = tmp_path / "invalid.sipl"
    file.write_text("begin X := end", encoding="utf-8")
    assert main(["check", str(file), "--json"]) == 2
    assert json.loads(capsys.readouterr().out)["error"] == "syntax"


def test_runtime_error_exit_code(tmp_path, capsys):
    file = tmp_path / "invalid.sipl"
    file.write_text("begin X := Y end", encoding="utf-8")
    assert main(["run", str(file)]) == 3
    assert "not defined" in capsys.readouterr().out


def test_invalid_state_value(tmp_path, capsys):
    file = tmp_path / "valid.sipl"
    file.write_text("begin skip end", encoding="utf-8")
    assert main(["run", str(file), "--state", "X=no"]) == 3
    assert "Invalid integer" in capsys.readouterr().out


def test_missing_file(capsys):
    assert main(["check", "/missing/sipl-file.sipl"]) == 3
    assert "No such file" in capsys.readouterr().out
