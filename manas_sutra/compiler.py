"""Compiler orchestration for Manas-Sutra."""

from __future__ import annotations

from dataclasses import dataclass

from .codegen import generate_python
from .graph import SemanticGraph
from .parser import ManasProgram, parse_source


@dataclass(frozen=True)
class CompilationResult:
    program: ManasProgram
    graph: SemanticGraph
    python: str


def compile_source(source: str) -> CompilationResult:
    """Run the v0.1 pipeline: parse, graph build, Python scaffold generation."""

    program = parse_source(source)
    graph = SemanticGraph.from_program(program)
    python = generate_python(program)
    return CompilationResult(program=program, graph=graph, python=python)
