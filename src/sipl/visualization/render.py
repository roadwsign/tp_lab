from __future__ import annotations

import html
import json
from dataclasses import fields, is_dataclass
from typing import Any

from lark import Token, Tree

from sipl import ast
from sipl.parser import ast_to_dict


def parse_tree_to_dict(node: Tree | Token, source: str | None = None) -> dict[str, Any]:
    if isinstance(node, Token):
        result: dict[str, Any] = {
            "type": "Token",
            "name": node.type,
            "value": str(node),
            "span": {
                "line": node.line,
                "column": node.column,
                "end_line": node.end_line,
                "end_column": node.end_column,
                "start_pos": node.start_pos,
                "end_pos": node.end_pos,
            },
        }
        if source is not None:
            result["source_fragment"] = source[node.start_pos:node.end_pos]
        return result
    children: list[Any] = [
        parse_tree_to_dict(child, source) if isinstance(child, (Tree, Token)) else child
        for child in node.children
    ]
    rule_result: dict[str, Any] = {
        "type": "Rule",
        "name": str(node.data),
        "span": {
            "line": node.meta.line,
            "column": node.meta.column,
            "end_line": node.meta.end_line,
            "end_column": node.meta.end_column,
            "start_pos": node.meta.start_pos,
            "end_pos": node.meta.end_pos,
        },
        "children": children,
    }
    if source is not None:
        rule_result["source_fragment"] = source[node.meta.start_pos:node.meta.end_pos]
    return rule_result


def parse_tree_text(node: Tree | Token, depth: int = 0) -> str:
    prefix = "  " * depth
    if isinstance(node, Token):
        return f"{prefix}{node.type}: {str(node)!r}"
    lines = [f"{prefix}{node.data}"]
    for child in node.children:
        lines.append(parse_tree_text(child, depth + 1) if isinstance(child, (Tree, Token)) else f"{prefix}  {child}")
    return "\n".join(lines)


def ast_text(node: Any, depth: int = 0) -> str:
    prefix = "  " * depth
    if isinstance(node, tuple):
        return "\n".join(ast_text(item, depth) for item in node)
    if not is_dataclass(node):
        return f"{prefix}{node!r}"
    values = []
    for item in fields(node):
        if item.name == "span":
            continue
        value = getattr(node, item.name)
        if is_dataclass(value) or isinstance(value, tuple):
            values.append(f"{prefix}  {item.name}:")
            values.append(ast_text(value, depth + 2))
        else:
            values.append(f"{prefix}  {item.name}: {value!r}")
    return f"{prefix}{type(node).__name__}\n" + "\n".join(values)


def _dot_nodes(tree: dict[str, Any], prefix: str = "n") -> tuple[list[str], list[str]]:
    nodes: list[str] = []
    edges: list[str] = []
    counter = [0]

    def visit(item: dict[str, Any], parent: str | None = None) -> None:
        identifier = f"{prefix}{counter[0]}"
        counter[0] += 1
        label = item.get("name", item.get("type", "Node"))
        if "value" in item:
            label = f"{label}: {item['value']}"
        span = item.get("span", {})
        tooltip = item.get("source_fragment", f"{span.get('line', 1)}:{span.get('column', 1)}")
        nodes.append(f'{identifier} [label="{_dot_escape(label)}", tooltip="{_dot_escape(str(tooltip))}"];')
        if parent:
            edges.append(f"{parent} -> {identifier};")
        for child in item.get("children", []):
            if isinstance(child, dict):
                visit(child, identifier)

    visit(tree)
    return nodes, edges


def _dot_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def to_dot(data: dict[str, Any], graph_name: str = "SIPL") -> str:
    nodes, edges = _dot_nodes(data)
    return "digraph " + graph_name + " {\n  node [shape=box];\n  " + "\n  ".join(nodes + edges) + "\n}\n"


def to_svg(data: dict[str, Any], title: str = "SIPL syntax tree") -> str:
    if "parse_tree" in data and "ast" in data and "children" not in data:
        data = {
            "type": "Comparison",
            "name": "Parse Tree ↔ AST",
            "children": [
                data["parse_tree"],
                ast_visual_data(data["ast"]),
            ],
        }
    nodes: list[tuple[str, int, int, int, str]] = []
    edges: list[tuple[int, int]] = []
    next_id = [0]

    def walk(item: dict[str, Any], depth: int, parent: int | None = None) -> None:
        index = next_id[0]
        next_id[0] += 1
        label = str(item.get("name", item.get("type", "Node")))
        if "value" in item:
            label += ": " + str(item["value"])
        nodes.append((label, depth, index, len(nodes), str(item.get("source_fragment", ""))))
        if parent is not None:
            edges.append((parent, index))
        for child in item.get("children", []):
            if isinstance(child, dict):
                walk(child, depth + 1, index)

    walk(data, 0)
    levels: dict[int, list[tuple[str, int, int, int, str]]] = {}
    for item in nodes:
        levels.setdefault(item[1], []).append(item)
    width = max(720, max((len(items) * 220 for items in levels.values()), default=720))
    height = max(160, (max(levels) + 1) * 110 + 40)
    positions: dict[int, tuple[int, int]] = {}
    for depth, items in levels.items():
        gap = width / (len(items) + 1)
        for i, (_, _, index, _, _) in enumerate(items, 1):
            positions[index] = (int(gap * i), 45 + depth * 110)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<title>{html.escape(title)}</title>',
        '<style>text{font:13px sans-serif}.node{fill:#f7f8fa;stroke:#354052;stroke-width:1.3}.edge{stroke:#65758b;stroke-width:1.2}</style>',
    ]
    for parent, child in edges:
        x1, y1 = positions[parent]
        x2, y2 = positions[child]
        parts.append(f'<line class="edge" x1="{x1}" y1="{y1 + 18}" x2="{x2}" y2="{y2 - 18}"/>')
    for label, depth, index, _, source_fragment in nodes:
        x, y = positions[index]
        safe = html.escape(label)
        source_title = html.escape(source_fragment)
        parts.append(f'<g><title>{source_title}</title><rect class="node" x="{x - 88}" y="{y - 18}" width="176" height="36" rx="5"/>')
        parts.append(f'<text x="{x}" y="{y + 5}" text-anchor="middle">{safe[:28]}</text></g>')
    parts.append("</svg>")
    return "\n".join(parts)

def comparison_html(parse_data: dict[str, Any], ast_data: dict[str, Any]) -> str:
    parse_svg = to_svg(parse_data, "SIPL Parse Tree")
    ast_svg = to_svg(ast_visual_data(ast_data), "SIPL AST")
    parse_json = html.escape(json.dumps(parse_data, ensure_ascii=False, indent=2))
    ast_json = html.escape(json.dumps(ast_data, ensure_ascii=False, indent=2))
    return (
        "<!doctype html><html lang='uk'><meta charset='utf-8'><title>SIPL Parse Tree та AST</title>"
        "<style>body{font:14px system-ui;margin:2rem;background:#fafbfc;color:#1f2328}"
        "main{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}"
        "section{min-width:0;background:#fff;border:1px solid #d0d7de;border-radius:8px;padding:1rem}"
        ".tree-box{overflow:auto;border:1px solid #eaeef2;border-radius:6px;padding:0.5rem;background:#fff}"
        "details{margin-top:0.75rem}summary{cursor:pointer;font-weight:600;color:#0969da}"
        "pre{background:#f4f5f7;padding:1rem;overflow:auto;white-space:pre-wrap;border-radius:6px;font-size:12px}"
        "@media(max-width:900px){main{grid-template-columns:1fr}}</style>"
        "<h1>Parse Tree ↔ AST</h1><main>"
        f"<section><h2>Parse Tree</h2><div class='tree-box'>{parse_svg}</div>"
        f"<details><summary>JSON + Source Spans</summary><pre>{parse_json}</pre></details></section>"
        f"<section><h2>AST</h2><div class='tree-box'>{ast_svg}</div>"
        f"<details><summary>JSON + Source Spans</summary><pre>{ast_json}</pre></details></section></main></html>"
    )

def ast_visual_data(node: Any) -> dict[str, Any]:
    if isinstance(node, dict):
        children = []
        for key, value in node.items():
            if key in {"span", "type", "source_fragment"}:
                continue
            if isinstance(value, dict):
                children.append({"type": "Field", "name": key, "children": [ast_visual_data(value)]})
            elif isinstance(value, list):
                children.append({"type": "Field", "name": key, "children": [ast_visual_data(item) for item in value]})
            elif isinstance(value, (str, int, bool)):
                children.append({"type": "Field", "name": f"{key}: {value}", "children": []})
        return {
            "type": "ASTNode",
            "name": node.get("type", "Node"),
            "source_fragment": node.get("source_fragment", ""),
            "children": children,
        }
    if isinstance(node, list):
        return {"type": "List", "name": "List", "children": [ast_visual_data(item) for item in node]}
    return {"type": "Value", "name": str(node), "children": []}


def ast_to_svg(node: ast.Program) -> str:
    return to_svg(ast_visual_data(ast_to_dict(node)), "SIPL AST")
