# Manas-Sutra v0.1 Design

Manas-Sutra starts as a deterministic intent-to-graph-to-code pipeline.

## Pipeline

```text
.msutra source
    -> parser
    -> canonical program
    -> semantic graph
    -> code generator
    -> executable scaffold
```

## Design rules

1. Human terms are only the inspection layer.
2. The canonical representation uses stable machine concepts.
3. Generated code must preserve constraints and verification requirements as metadata.
4. The compiler should fail clearly on ambiguous source.
5. Advanced AI synthesis belongs behind the code generation interface, not inside the parser.

## Future work

- Add a JSON Schema for canonical programs.
- Add planners that decompose goals into subgoals.
- Add domain generators for APIs, data transforms, and scheduling.
- Add property-based tests and static analysis hooks.
- Add a multi-agent execution protocol for planner/coder/reviewer/verifier roles.
