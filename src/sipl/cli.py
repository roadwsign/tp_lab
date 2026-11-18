from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from sipl import __version__
from sipl.interpreter import SIPLRuntimeError, execute
from sipl.parser import SIPLSyntaxError, ast_to_dict, parse, parse_tree
from sipl.visualization import (
    ast_text,
    ast_visual_data,
    comparison_html,
    parse_tree_text,
    parse_tree_to_dict,
    to_dot,
    to_svg,
)


def _state(values: list[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"Invalid state value {item!r}; expected NAME=INTEGER")
        name, raw = item.split("=", 1)
        if not name.isidentifier():
            raise ValueError(f"Invalid variable name {name!r}")
        try:
            result[name] = int(raw)
        except ValueError:
            raise ValueError(f"Invalid integer value in {item!r}") from None
    return result


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _write(value: str) -> None:
    sys.stdout.write(value)
    if not value.endswith("\n"):
        sys.stdout.write("\n")


def _parse_command(args: argparse.Namespace) -> int:
    source = _read(args.file)
    tree = parse_tree(source)
    program = parse(source)
    tree_data = parse_tree_to_dict(tree, source)
    ast_data = ast_to_dict(program, source)
    text_value: str
    if args.view == "parse-tree":
        data: Any = tree_data
        text_value = parse_tree_text(tree)
    elif args.view == "ast":
        data = ast_data
        text_value = ast_text(program)
    else:
        data = {"parse_tree": tree_data, "ast": ast_data}
        text_value = comparison_html(tree_data, ast_data)
    visual_data = ast_visual_data(ast_data) if args.view == "ast" else data
    if args.format == "json":
        _write(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.format == "dot":
        _write(to_dot(visual_data))
    elif args.format == "svg":
        _write(to_svg(visual_data))
    elif args.format == "html":
        _write(text_value if args.view == "comparison" else comparison_html(tree_data, ast_data))
    else:
        _write(text_value)
    return 0


def _check_command(args: argparse.Namespace) -> int:
    parse(_read(args.file))
    result = {"valid": True, "message": "SIPL program is syntactically correct"}
    _write(json.dumps(result, ensure_ascii=False) if args.json else "SIPL program is syntactically correct")
    return 0


def _run_command(args: argparse.Namespace, trace: bool = False) -> int:
    program = parse(_read(args.file))
    result = execute(program, _state(args.state), args.max_steps, trace=trace)
    payload = result.to_dict() if trace else {"state": result.state, "steps": result.steps}
    _write(json.dumps(payload, ensure_ascii=False, indent=2) if trace else json.dumps(result.state, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sipl", description="SIPL Language Toolkit")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_parser = subparsers.add_parser("parse")
    parse_parser.add_argument("file", nargs="?", default="-")
    parse_parser.add_argument("--view", choices=("parse-tree", "ast", "comparison"), default="ast")
    parse_parser.add_argument("--format", choices=("text", "json", "dot", "svg", "html"), default="text")
    parse_parser.set_defaults(handler=_parse_command)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("file", nargs="?", default="-")
    check_parser.add_argument("--json", action="store_true")
    check_parser.set_defaults(handler=_check_command)

    for command in ("run", "trace"):
        run_parser = subparsers.add_parser(command)
        run_parser.add_argument("file", nargs="?", default="-")
        run_parser.add_argument("--state", action="append", default=[])
        run_parser.add_argument("--max-steps", type=int, default=100_000)
        run_parser.add_argument("--json", action="store_true")
        run_parser.set_defaults(handler=lambda args, is_trace=command == "trace": _run_command(args, is_trace))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except SIPLSyntaxError as error:
        payload = {
            "error": "syntax",
            "message": error.message,
            "line": error.line,
            "column": error.column,
            "expected": error.expected,
        }
        _write(json.dumps(payload, ensure_ascii=False) if getattr(args, "json", False) else f"{error.message} at line {error.line}, column {error.column}")
        return 2
    except (SIPLRuntimeError, ValueError, OSError) as error:
        payload = {"error": "execution", "message": str(error)}
        _write(json.dumps(payload, ensure_ascii=False) if getattr(args, "json", False) else str(error))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
