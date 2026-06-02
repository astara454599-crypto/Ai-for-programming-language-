# SUTRA-AI Formal Design v0.1

SUTRA-AI moves the repository beyond a keyword DSL. It defines a five-layer
cognitive computation protocol that can still compile into ordinary execution
artifacts.

## Layers

1. **VAAKYA (वाक्य)** — human surface grammar. This is the `.sutra` syntax that
   humans inspect and AIs can generate.
2. **SIDDHA (सिद्ध)** — canonical semantic form. The parser resolves the surface
   grammar into stable JSON-serializable machine concepts.
3. **JALA (जाल)** — semantic graph. The compiler builds typed nodes and causal
   edges around goals, constraints, knowledge, proof requirements, and outputs.
4. **VIVEKA (विवेक)** — reasoning and synthesis. The current prototype uses a
   deterministic generator registry; future versions can route through planners,
   proof engines, and multi-agent synthesis.
5. **KARMA (कर्म)** — execution targets. v0.1 targets Python, but the same
   canonical form can later target Rust, Lean proofs, CUDA kernels, or agent APIs.

## Cognitive contract syntax

```sutra
◈ TATVA [SumNumbers] {
  AGAMA {
    numbers: Evidence<List<Number>, 1.0>
  }

  BANDHANA {
    numeric_only: ENFORCE(all_numeric(numbers))
    accuracy: MANDATE(total = Σ(numbers))
  }

  PRAMAN {
    unit: Proof<SumCorrect, "unit-test">
  }

  PHALA {
    total: Verified<Number>
  }
}
```

## Cognitive primitives

| Primitive | Meaning | Canonical section |
| --- | --- | --- |
| `TATVA` | bounded cognitive contract | `goal` / `contract` |
| `AGAMA` | input/evidence declarations | `inputs` |
| `BANDHANA` | hard/soft/modal constraints | `constraints` |
| `JNANA` | knowledge and ontology references | `knowledge` |
| `ANVESHANA` | search strategy and reasoning posture | `search` |
| `PRAMAN` | proof and verification requirements | `verification` |
| `SAMVAD` | multi-agent coordination | `agents` |
| `SMRITI` | four-tier agent memory | `memory` |
| `VIKASA` | gated self-evolution protocol | `self_evolution` |
| `PHALA` | verified output declarations | `outputs` |

## Current implementation status

The repository now accepts both legacy `.msutra` section syntax and formal
SUTRA-AI `TATVA` contracts. Both routes produce one `ManasProgram`, one Siddha
JSON representation, one Jala semantic graph, and one Python execution artifact.


## Additional specification documents

- `docs/cognitive-type-system.md` defines `Goal<T>`, `Evidence<T,p>`, `Proof<T,S>`, `Uncertain<T,σ>`, `Causal<A→B,γ>`, `Temporal<T,Δt>`, `Verified<T>`, `Unsafe<T>`, and the type algebra.
- `docs/samvad-memory-vikasa.md` captures multi-agent consensus, the four-tier memory architecture, and the safe self-evolution gates from the reference design.
- `docs/roadmap.md` records the 30-month roadmap and open research questions: completeness, decidability, Byzantine bounds, self-reference, temporal types, and VIKASA convergence.
