"""Parser for the Manas-Sutra human inspection layer.

The syntax is intentionally small in v0.1: each section begins with a known
Sanskrit-inspired heading followed by indented items. The parser produces a
canonical ``ManasProgram`` that downstream graph and code generation stages can
consume deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


SECTION_ALIASES = {
    "lakshya": "goal",
    "goal": "goal",
    "dravya": "inputs",
    "input": "inputs",
    "inputs": "inputs",
    "bandhana": "constraints",
    "constraint": "constraints",
    "constraints": "constraints",
    "pramana": "verification",
    "verification": "verification",
    "verify": "verification",
    "phala": "outputs",
    "output": "outputs",
    "outputs": "outputs",
    "smriti": "memory",
    "memory": "memory",
    "sandeha": "uncertainty",
    "uncertainty": "uncertainty",
    "sahakara": "agents",
    "agents": "agents",
    "agent": "agents",
}

REQUIRED_SECTIONS = ("goal", "outputs")
LIST_SECTIONS = (
    "inputs",
    "constraints",
    "verification",
    "outputs",
    "memory",
    "uncertainty",
    "agents",
)


@dataclass(frozen=True)
class ManasProgram:
    """Canonical parsed representation of a Manas-Sutra source file."""

    goal: str
    inputs: tuple[str, ...] = field(default_factory=tuple)
    constraints: tuple[str, ...] = field(default_factory=tuple)
    verification: tuple[str, ...] = field(default_factory=tuple)
    outputs: tuple[str, ...] = field(default_factory=tuple)
    memory: tuple[str, ...] = field(default_factory=tuple)
    uncertainty: tuple[str, ...] = field(default_factory=tuple)
    agents: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable canonical form."""

        return {
            "goal": self.goal,
            "inputs": list(self.inputs),
            "constraints": list(self.constraints),
            "verification": list(self.verification),
            "outputs": list(self.outputs),
            "memory": list(self.memory),
            "uncertainty": list(self.uncertainty),
            "agents": list(self.agents),
        }


class ParseError(ValueError):
    """Raised when a Manas-Sutra document is invalid."""


def parse_source(source: str) -> ManasProgram:
    """Parse Manas-Sutra text into a canonical program.

    Comments begin with ``#``. Blank lines are ignored. Section names are
    case-insensitive and may use either Sanskrit-inspired names or English
    aliases.
    """

    sections: dict[str, list[str]] = {name: [] for name in LIST_SECTIONS}
    goal_values: list[str] = []
    current_section: str | None = None

    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        line = _strip_comment(raw_line).rstrip()
        if not line.strip():
            continue

        stripped = line.strip()
        if stripped.endswith(":") and not stripped.startswith(("-", "*")):
            section_name = stripped[:-1].strip().lower()
            current_section = SECTION_ALIASES.get(section_name)
            if current_section is None:
                known = ", ".join(sorted(SECTION_ALIASES))
                raise ParseError(
                    f"Unknown section '{stripped[:-1]}' on line {line_number}. "
                    f"Known sections: {known}."
                )
            continue

        if current_section is None:
            raise ParseError(
                f"Line {line_number} contains an item before any section: {stripped!r}."
            )

        item = _normalize_item(stripped)
        if not item:
            continue

        if current_section == "goal":
            goal_values.append(item)
        else:
            sections[current_section].append(item)

    if not goal_values:
        raise ParseError("Missing required section Lakshya/Goal with one goal item.")
    if len(goal_values) > 1:
        raise ParseError("Lakshya/Goal must contain exactly one goal item in v0.1.")
    if not sections["outputs"]:
        raise ParseError("Missing required section Phala/Output with at least one output item.")

    return ManasProgram(
        goal=goal_values[0],
        inputs=_unique_preserving_order(sections["inputs"]),
        constraints=_unique_preserving_order(sections["constraints"]),
        verification=_unique_preserving_order(sections["verification"]),
        outputs=_unique_preserving_order(sections["outputs"]),
        memory=_unique_preserving_order(sections["memory"]),
        uncertainty=_unique_preserving_order(sections["uncertainty"]),
        agents=_unique_preserving_order(sections["agents"]),
    )


def _strip_comment(line: str) -> str:
    return line.split("#", 1)[0]


def _normalize_item(item: str) -> str:
    item = item.removeprefix("-").removeprefix("*").strip()
    return " ".join(item.split())


def _unique_preserving_order(items: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return tuple(unique)
