"""Semantic graph representation for Manas-Sutra programs."""

from __future__ import annotations

from dataclasses import dataclass

from .parser import ManasProgram


@dataclass(frozen=True)
class GraphNode:
    id: str
    kind: str
    label: str


@dataclass(frozen=True)
class GraphEdge:
    source: str
    relation: str
    target: str


@dataclass(frozen=True)
class SemanticGraph:
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]

    @classmethod
    def from_program(cls, program: ManasProgram) -> "SemanticGraph":
        """Build a typed graph from a parsed program."""

        nodes = [GraphNode("goal:0", "goal", program.goal)]
        edges: list[GraphEdge] = []

        section_map = {
            "inputs": (program.inputs, "input", "uses"),
            "constraints": (program.constraints, "constraint", "constrained_by"),
            "verification": (program.verification, "verification", "verified_by"),
            "outputs": (program.outputs, "output", "produces"),
            "memory": (program.memory, "memory", "remembers"),
            "uncertainty": (program.uncertainty, "uncertainty", "has_uncertainty"),
            "agents": (program.agents, "agent", "coordinated_with"),
        }

        for section, (items, kind, relation) in section_map.items():
            for index, item in enumerate(items):
                node_id = f"{section}:{index}"
                nodes.append(GraphNode(node_id, kind, item))
                edges.append(GraphEdge("goal:0", relation, node_id))

        return cls(tuple(nodes), tuple(edges))

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable graph."""

        return {
            "nodes": [node.__dict__ for node in self.nodes],
            "edges": [edge.__dict__ for edge in self.edges],
        }

    def render_tree(self) -> str:
        """Render a compact tree for human inspection."""

        goal = next(node for node in self.nodes if node.id == "goal:0")
        labels_by_id = {node.id: node for node in self.nodes}
        lines = [f"Goal: {goal.label}"]
        for edge in self.edges:
            node = labels_by_id[edge.target]
            lines.append(f" ├─ {node.kind}: {node.label} [{edge.relation}]")
        return "\n".join(lines)
