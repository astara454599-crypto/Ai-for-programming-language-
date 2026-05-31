"""Command line interface for Manas-Sutra."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compiler import compile_source
from .parser import ParseError


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile Manas-Sutra intent files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_parser = subparsers.add_parser("compile", help="Compile a .msutra file.")
    compile_parser.add_argument("source", type=Path)
    compile_parser.add_argument("--out", type=Path, help="Write generated Python to this path.")
    compile_parser.add_argument(
        "--graph-json", type=Path, help="Write semantic graph JSON to this path."
    )
    compile_parser.add_argument(
        "--show-tree", action="store_true", help="Print a readable semantic tree."
    )

    args = parser.parse_args()

    try:
        source = args.source.read_text(encoding="utf-8")
        result = compile_source(source)
    except (OSError, ParseError) as exc:
        parser.error(str(exc))
        return 2

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(result.python, encoding="utf-8")
    else:
        print(result.python)

    if args.graph_json:
        args.graph_json.parent.mkdir(parents=True, exist_ok=True)
        args.graph_json.write_text(
            json.dumps(result.graph.to_dict(), indent=2), encoding="utf-8"
        )

    if args.show_tree:
        print(result.graph.render_tree())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
