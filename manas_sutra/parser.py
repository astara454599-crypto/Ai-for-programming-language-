"""Parser for Manas-Sutra and SUTRA-AI intent sources.

Two compatible surface grammars are supported:

* Manas-Sutra v0.1 section files such as ``Lakshya:``, ``Dravya:``, and
  ``Phala:``.
* SUTRA-AI cognitive contracts such as ``◈ TATVA [Name] { ... }`` with
  ``AGAMA``, ``BANDHANA``, ``PRAMAN``, ``SAMVAD``, and ``PHALA`` blocks.

Both forms produce the same canonical ``ManasProgram`` so downstream graph and
code generation layers can operate on stable machine concepts instead of human
surface syntax.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Mapping


SECTION_ALIASES = {
    "lakshya": "goal",
    "goal": "goal",
    "dravya": "inputs",
    "agama": "inputs",
    "input": "inputs",
    "inputs": "inputs",
    "bandhana": "constraints",
    "constraint": "constraints",
    "constraints": "constraints",
    "pramana": "verification",
    "praman": "verification",
    "verification": "verification",
    "verify": "verification",
    "phala": "outputs",
    "output": "outputs",
    "outputs": "outputs",
    "smriti": "memory",
    "memory": "memory",
    "jnana": "knowledge",
    "knowledge": "knowledge",
    "sandeha": "uncertainty",
    "uncertainty": "uncertainty",
    "sahakara": "agents",
    "samvad": "agents",
    "agents": "agents",
    "agent": "agents",
    "anveshana": "search",
    "search": "search",
}

SUTRA_BLOCK_ALIASES = {
    "AGAMA": "inputs",
    "BANDHANA": "constraints",
    "JNANA": "knowledge",
    "ANVESHANA": "search",
    "PRAMAN": "verification",
    "PRAMANA": "verification",
    "SAMVAD": "agents",
    "PHALA": "outputs",
}

LIST_SECTIONS = (
    "inputs",
    "constraints",
    "verification",
    "outputs",
    "memory",
    "knowledge",
    "uncertainty",
    "agents",
    "search",
)

SUTRA_LAYER_CONTEXT = {
    "vaakya": "human surface grammar",
    "siddha": "canonical semantic form",
    "jala": "semantic knowledge graph",
    "viveka": "reasoning and synthesis engine",
    "karma": "adaptive execution target",
}


@dataclass(frozen=True)
class ManasProgram:
    """Canonical parsed representation of a Manas-Sutra/SUTRA-AI source file."""

    goal: str
    inputs: tuple[str, ...] = field(default_factory=tuple)
    constraints: tuple[str, ...] = field(default_factory=tuple)
    verification: tuple[str, ...] = field(default_factory=tuple)
    outputs: tuple[str, ...] = field(default_factory=tuple)
    memory: tuple[str, ...] = field(default_factory=tuple)
    knowledge: tuple[str, ...] = field(default_factory=tuple)
    uncertainty: tuple[str, ...] = field(default_factory=tuple)
    agents: tuple[str, ...] = field(default_factory=tuple)
    search: tuple[str, ...] = field(default_factory=tuple)
    dialect: str = "manas-sutra-v0.1"
    contract: str | None = None
    raw_sections: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable canonical Siddha representation."""

        return {
            "@context": "https://sutra-ai.local/context/v0.1",
            "protocol": "SUTRA-AI",
            "dialect": self.dialect,
            "contract": self.contract or self.goal,
            "layers": SUTRA_LAYER_CONTEXT,
            "goal": self.goal,
            "inputs": list(self.inputs),
            "constraints": list(self.constraints),
            "verification": list(self.verification),
            "outputs": list(self.outputs),
            "memory": list(self.memory),
            "knowledge": list(self.knowledge),
            "uncertainty": list(self.uncertainty),
            "agents": list(self.agents),
            "search": list(self.search),
            "raw_sections": {
                name: list(items) for name, items in self.raw_sections.items()
            },
        }


class ParseError(ValueError):
    """Raised when a Manas-Sutra document is invalid."""


def parse_source(source: str) -> ManasProgram:
    """Parse intent text into a canonical program.

    Comments begin with ``#``. Blank lines are ignored. The parser auto-detects
    SUTRA-AI cognitive-contract syntax when it sees ``TATVA``.
    """

    if _looks_like_sutra_contract(source):
        return _parse_sutra_contract(source)
    return _parse_section_source(source)


def _parse_section_source(source: str) -> ManasProgram:
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

    return _build_program(
        goal=goal_values[0],
        sections=sections,
        dialect="manas-sutra-v0.1",
        contract=goal_values[0],
    )


def _parse_sutra_contract(source: str) -> ManasProgram:
    header_match = re.search(r"(?:◈\s*)?TATVA\s*\[\s*([^\]]+)\s*\]\s*\{", source)
    if not header_match:
        raise ParseError("SUTRA-AI source must start with a TATVA [ContractName] block.")

    contract_name = header_match.group(1).strip()
    sections: dict[str, list[str]] = {name: [] for name in LIST_SECTIONS}
    current_section: str | None = None
    brace_depth = 0

    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        line = _strip_comment(raw_line).strip()
        if not line:
            continue

        if re.match(r"(?:◈\s*)?TATVA\s*\[", line):
            brace_depth += line.count("{") - line.count("}")
            continue

        block_match = re.match(r"([A-Z][A-Z_]*)(?:\s*\[[^\]]+\])?\s*\{\s*$", line)
        if block_match:
            block_name = block_match.group(1)
            current_section = SUTRA_BLOCK_ALIASES.get(block_name)
            if current_section is None:
                known = ", ".join(sorted(SUTRA_BLOCK_ALIASES))
                raise ParseError(
                    f"Unknown SUTRA-AI block '{block_name}' on line {line_number}. "
                    f"Known blocks: {known}."
                )
            brace_depth += 1
            continue

        if line == "}":
            if current_section is not None:
                current_section = None
            brace_depth = max(0, brace_depth - 1)
            continue

        if current_section is None:
            continue

        item = _normalize_item(line.rstrip(","))
        if item:
            sections[current_section].append(item)

    if not sections["outputs"]:
        raise ParseError("SUTRA-AI TATVA must contain PHALA with at least one output.")

    goal = contract_name
    if sections["search"]:
        goal = _derive_goal_from_search(contract_name, sections["search"])

    return _build_program(
        goal=goal,
        sections=sections,
        dialect="sutra-ai-v0.1",
        contract=contract_name,
    )


def _build_program(
    *, goal: str, sections: dict[str, list[str]], dialect: str, contract: str
) -> ManasProgram:
    raw_sections = {
        name: _unique_preserving_order(items) for name, items in sections.items() if items
    }
    return ManasProgram(
        goal=goal,
        inputs=_field_names(raw_sections.get("inputs", ())),
        constraints=_unique_preserving_order(raw_sections.get("constraints", ())),
        verification=_unique_preserving_order(raw_sections.get("verification", ())),
        outputs=_field_names(raw_sections.get("outputs", ())),
        memory=_unique_preserving_order(raw_sections.get("memory", ())),
        knowledge=_unique_preserving_order(raw_sections.get("knowledge", ())),
        uncertainty=_unique_preserving_order(raw_sections.get("uncertainty", ())),
        agents=_unique_preserving_order(raw_sections.get("agents", ())),
        search=_unique_preserving_order(raw_sections.get("search", ())),
        dialect=dialect,
        contract=contract,
        raw_sections=raw_sections,
    )


def _looks_like_sutra_contract(source: str) -> bool:
    return bool(re.search(r"(?:^|\n)\s*(?:◈\s*)?TATVA\s*\[", source))


def _derive_goal_from_search(contract_name: str, search_items: list[str]) -> str:
    for item in search_items:
        if item.lower().startswith("goal:"):
            return _normalize_field_name(item.split(":", 1)[1])
    return contract_name


def _field_names(items: Iterable[str]) -> tuple[str, ...]:
    return _unique_preserving_order(_normalize_field_name(item) for item in items)


def _normalize_field_name(item: str) -> str:
    if ":" in item:
        item = item.split(":", 1)[0]
    if "=" in item:
        item = item.split("=", 1)[0]
    item = item.strip()
    return " ".join(item.split())


def _strip_comment(line: str) -> str:
    return line.split("#", 1)[0]


def _normalize_item(item: str) -> str:
    item = item.removeprefix("-").removeprefix("*").strip()
    return " ".join(item.split())


def _unique_preserving_order(items: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if not item:
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return tuple(unique)
