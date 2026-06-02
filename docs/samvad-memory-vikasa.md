# SAMVAD, SMRITI, and VIKASA

The screenshots describe three capabilities that make SUTRA-AI more than a code
syntax: multi-agent consensus, structured memory, and controlled self-evolution.
This repository now preserves these blocks in the canonical form and Jala graph.

## SAMVAD — multi-agent coordination

`SAMVAD` makes collaboration a language primitive. A contract can declare agent
roles, trust levels, vote weights, communication topology, consensus thresholds,
and failure escalation.

```sutra
SAMVAD {
  AGENT NidanAI { bhumika: Diagnosis, vishwas: 0.90, votes: 1 }
  AGENT Specialist { bhumika: DomainExpert, vishwas: 0.95, votes: 2 }
  AGENT DevilAI { bhumika: Falsification, vishwas: 0.99, votes: 3 }
  nirnaya: WeightedVoting(supermajority=0.75)
  apavad: ESCALATE_TO_HUMAN
}
```

Consensus patterns from the design:

- **Sequential**: each agent waits for the previous output.
- **Parallel**: independent agents work simultaneously.
- **Cyclic**: agents iterate until convergence.
- **Byzantine**: k-of-n agreement prevents single-agent corruption.
- **Adversarial**: a Devil AI tries to falsify proposals before acceptance.
- **Hierarchical**: parent agents delegate and aggregate subtasks.

## SMRITI — four-tier agent memory

`SMRITI` separates memory into four tiers:

1. **Episodic**: recent cases, usually with sliding-window expiry.
2. **Semantic**: versioned domain knowledge.
3. **Procedural**: learned strategies and workflows.
4. **Working**: current task context.

The memory operations in the design are `LEARN`, `FORGET`, `SHARE`, `VERIFY`, and
`REDACT`. The parser preserves these declarations so later privacy and memory
engines can enforce differential privacy and knowledge freshness.

## VIKASA — controlled self-evolution

`VIKASA` is intentionally treated as dangerous. A proposal may extend surface
syntax, search heuristics, or knowledge registrations, but must not weaken core
constraints, proof requirements, Byzantine consensus rules, human override, or
scope boundaries.

Mandatory gates from the design:

1. AI proposes a `CognitiveContract<ProposedChange>`.
2. Lean/Coq-style proof shows no safety property is weakened.
3. Independent agents reach Byzantine consensus.
4. Adversarial testing tries to break the proposal.
5. Sandbox isolation runs with no production access.
6. Human review is mandatory.
7. Staged rollout proceeds with automatic rollback.
8. Every step is recorded in an immutable audit log.
