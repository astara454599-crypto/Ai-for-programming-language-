# Manas-Sutra

Manas-Sutra / SUTRA-AI is an experimental AI-native cognitive computation protocol prototype. It is not meant to replace Python, Rust, or JavaScript. Instead, it starts with a compact intent language that describes goals, inputs, constraints, verification needs, and desired outputs, then converts that intent into a typed semantic graph and starter executable code.

This repository contains the first MVP:

- a Sanskrit-inspired human inspection layer;
- a deterministic parser for `.msutra` files and formal `.sutra` TATVA contracts;
- a canonical semantic graph representation;
- a small Python code generator for data/API oriented tasks;
- tests and examples that demonstrate the full flow.

## Example

```text
Lakshya:
    CreateTodoAPI

Dravya:
    User
    Task

Bandhana:
    AuthenticationRequired
    StoreDataInDatabase
    UserCanOnlyAccessOwnTasks

Pramana:
    UnitTests
    SecurityReview

Phala:
    FastAPIApplication
```

Compile it with:

```bash
python -m manas_sutra compile examples/todo_api.msutra --out generated/todo_api.py
```

## Core terms

| Term | Machine concept | Meaning |
| --- | --- | --- |
| `Lakshya` | `goal` | Desired task or objective |
| `Dravya` | `inputs` | Entities, materials, or data used by the task |
| `Bandhana` | `constraints` | Rules that must not be violated |
| `Pramana` | `verification` | Required checks, tests, or proofs |
| `Phala` | `outputs` | Desired artifact or result |
| `Smriti` | `memory` | Reusable prior knowledge or patterns |
| `Sandeha` | `uncertainty` | Unknowns or confidence notes |
| `Sahakara` | `agents` | Cooperating roles or AI agents |

## Why this design?

The project deliberately separates the language into three layers:

1. **Human layer**: readable `.msutra` files inspired by precise Sanskrit-style labels.
2. **AI layer**: a typed semantic graph that is easier for agents to inspect, transform, and verify.
3. **Execution layer**: code generation into normal languages, starting with Python.

The MVP is intentionally small. It proves the language pipeline before adding advanced synthesis, solver-backed planning, formal verification, or multi-agent runtimes.

## Use it now

Start with the runnable `SumNumbers` example in either legacy Manas-Sutra or formal SUTRA-AI syntax:

```bash
python -m manas_sutra inspect examples/sutra_sum.sutra
python -m manas_sutra compile examples/sutra_sum.sutra --out generated/sutra_sum.py --graph-json generated/sutra_sum.graph.json --show-tree
```

Then run the generated function:

```bash
python - <<'PY'
from generated.sutra_sum import sum_numbers
print(sum_numbers(numbers=[1, 2, 3, 4, 5]).outputs)
PY
```

See `docs/quickstart.md` for the walkthrough and `docs/sutra-ai-formal-design.md` for the formal design.

## Development

Run tests with:

```bash
python -m unittest discover -s tests
```
