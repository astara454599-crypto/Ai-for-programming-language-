# Manas-Sutra

Manas-Sutra / SUTRA-AI is an experimental AI-native cognitive computation protocol prototype. It is not meant to replace Python, Rust, or JavaScript. Instead, it starts with a compact intent language that describes goals, inputs, constraints, verification needs, and desired outputs, then converts that intent into a typed semantic graph and starter executable code.

This repository contains the first MVP:

- a Sanskrit-inspired human inspection layer;
- a deterministic parser for `.msutra` files and formal `.sutra` TATVA contracts;
- a canonical semantic graph representation with knowledge, search, memory, agent, self-evolution, and cognitive-type nodes;
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
result = sum_numbers(numbers=[1, 2, 3, 4, 5])
print(result.outputs["total"].value)
PY
```

If you want to publish it, create an empty GitHub repository and run `git remote add origin <repo-url>` followed by `git push -u origin work`. See `docs/quickstart.md` for the walkthrough, `docs/sutra-ai-formal-design.md` for the formal design, `docs/cognitive-type-system.md` for epistemic types, `docs/samvad-memory-vikasa.md` for multi-agent/memory/self-evolution semantics, and `docs/roadmap.md` for the 30-month plan.

## VIVEKA layer: LLM synthesis

The deterministic compiler is still available, but the VIVEKA layer can now send
a parsed SUTRA-AI contract/JALA graph to OpenRouter and request an implementation.
A safety backend must be running locally. Contact the maintainer for access.
The default model is `mistralai/mistral-7b-instruct`, which is free on OpenRouter.
Create a key at https://openrouter.ai/keys, then set it:

```bash
export OPENROUTER_API_KEY=your_key_here
python -m manas_sutra.viveka examples/sutra_sum.sutra --out generated/viveka_sum.py
```

To inspect the exact structured prompt input without calling the API, run:

```bash
python -m manas_sutra.viveka examples/sutra_sum.sutra --print-spec
```

VIVEKA uses `mistralai/mistral-7b-instruct` by default and prompts the model to
return only valid Python code that integrates with `manas_sutra.runtime` types
such as `Evidence`, `ProofCertificate`, `Verified`, and `Unsafe`.

## Development

Run tests with:

```bash
python -m unittest discover -s tests
```
