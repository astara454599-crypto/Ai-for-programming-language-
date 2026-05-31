# Quickstart: Use Manas-Sutra Now

This project is now usable as a small local prototype. The current flow is:

```text
write intent in .msutra or .sutra
    -> inspect semantic graph
    -> compile to Python
    -> run the generated Python function
```

## 1. Inspect an intent file

```bash
python -m manas_sutra inspect examples/sutra_sum.sutra
```

This prints the canonical program JSON and the semantic tree. Use this step to
check whether the AI/human-readable layer was understood correctly.

## 2. Compile intent to Python

```bash
python -m manas_sutra compile examples/sutra_sum.sutra --out generated/sutra_sum.py --graph-json generated/sutra_sum.graph.json --show-tree
```

This creates two artifacts:

- `generated/sutra_sum.py`: executable Python generated from the intent;
- `generated/sutra_sum.graph.json`: machine-readable semantic graph.

## 3. Run the generated function

```bash
python - <<'PY'
from generated.sutra_sum import describe_spec, sum_numbers

print(describe_spec())
result = sum_numbers(numbers=[1, 2, 3, 4, 5])
print(result.outputs)
print(result.notes)
PY
```

Expected output includes:

```text
{'total': 15}
```

## How it is going

The language is in the **v0.1 prototype stage**. It can already parse intent,
create a typed semantic graph, generate Python, and execute one deterministic
built-in generator for formal `TATVA [SumNumbers]` contracts. Unknown goals still compile into safe
scaffolds that preserve constraints and verification metadata.

## What to try next

1. Copy `examples/sum_numbers.msutra` and change the goal, inputs, constraints,
   and outputs.
2. Run `inspect` to verify the semantic graph.
3. Run `compile` to produce Python.
4. Add a domain generator in `manas_sutra/codegen.py` when you want the compiler
   to execute a new kind of goal instead of producing a scaffold.
