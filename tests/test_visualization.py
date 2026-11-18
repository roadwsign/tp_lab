from sipl.parser import ast_to_dict, parse, parse_tree
from sipl.visualization import (
    ast_text,
    comparison_html,
    parse_tree_text,
    parse_tree_to_dict,
    to_dot,
    to_svg,
)


def test_parse_tree_json_and_text():
    tree = parse_tree("begin skip end")
    data = parse_tree_to_dict(tree, "begin skip end")
    assert data["name"] == "start"
    assert data["source_fragment"] == "begin skip end"
    assert "skip_statement" in parse_tree_text(tree)


def test_ast_json_and_text():
    program = parse("begin X := 2 end")
    data = ast_to_dict(program, "begin X := 2 end")
    assert data["type"] == "Program"
    assert data["source_fragment"] == "begin X := 2 end"
    assert data["span"]["line"] == 1
    rendered = ast_text(program)
    assert "Assignment" in rendered
    assert "\\n" not in rendered
    assert "Program\n" in rendered


def test_dot_and_svg_exports():
    data = parse_tree_to_dict(parse_tree("begin skip end"))
    dot = to_dot(data)
    assert "digraph" in dot
    assert dot.startswith("digraph SIPL {\n")
    assert dot.endswith("\n}\n")
    assert len(dot.splitlines()) > 3
    assert "<svg" in to_svg(data)


def test_comparison_html():
    source = "begin skip end"
    result = comparison_html(parse_tree_to_dict(parse_tree(source)), ast_to_dict(parse(source)))
    assert "Parse Tree" in result
    assert "AST" in result
