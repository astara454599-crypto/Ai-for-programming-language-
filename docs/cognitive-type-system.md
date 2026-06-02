# Cognitive Type System

SUTRA-AI types classify epistemic states rather than only data shapes. A field is
not merely a `string` or `list`; it may be evidence, proof, uncertainty, causal
structure, temporal validity, agent belief, or redacted private knowledge.

## Primitive cognitive types

| Type | Meaning | Example |
| --- | --- | --- |
| `Goal<T>` | verifiable objective targeting `T` | `Goal<OptimalDrugCandidate>` |
| `Evidence<T, p>` | claim `T` with probability `p ∈ [0,1]` | `Evidence<CancerDiagnosis, 0.94>` |
| `Proof<T, Standard>` | `T` verified to a named standard | `Proof<AlgorithmCorrect, "ISO-9001">` |
| `Uncertain<T, σ>` | value with uncertainty spread `σ` | `Uncertain<PlasmaTemperature, σ=150K>` |
| `Causal<A → B, γ>` | causal relation with strength `γ` | `Causal<Smoke → Fire, 0.87>` |
| `Temporal<T, Δt>` | value valid for a time interval | `Temporal<MarketQuote, "5min">` |
| `Agent<Role, T>` | agent playing a role over `T` | `Agent<Verifier, DiagnosisResult>` |
| `Verified<T>` | passed all `PRAMAN` requirements | `Verified<SafeMolecule>` |
| `Contested<T>` | conflicting evidence remains unresolved | `Contested<EfficacyStudy>` |
| `Unsafe<T>` | must not be used until verified | `Unsafe<GeneratedCode>` |
| `Redacted<T>` | private data after differential privacy | `Redacted<PatientRecord, ε=0.1>` |
| `Known<T, Agent>` | belief state of an agent | `Known<Diagnosis, MedicalAI>` |

## Type algebra

| Operator | Meaning | Example |
| --- | --- | --- |
| `T ⊗ U` | product: requires both `T` and `U` | `Evidence<D, 0.9> ⊗ Proof<Safety, "ISO">` |
| `T ⊕ U` | sum: accepts either `T` or `U` | `Verified<Output> ⊕ Contested<Output>` |
| `T → U` | implication: `T` guarantees `U` | `Proof<Input, S> → Verified<Output>` |
| `⊥<T>` | negation: never `T` | `⊥<Unsafe<Output>>` |
| `∀T ∈ Dataset` | universal claim over a dataset | `Evidence<T, p ≥ 0.85>` |
| `∃T` | at least one verified instance exists | `∃T: Verified<T> ∧ Optimal<T>` |

## Selected inference rules

1. Sufficient evidence plus required proof strategy produces `Verified<T>`.
2. `Contested<T>` blocks verification unless explicitly resolved.
3. Causal relations compose transitively with degraded confidence.
4. Expired `Temporal<T, Δt>` values decay into `Uncertain<T, σ → ∞>`.
5. `Unsafe<T>` propagates to all downstream outputs until a `PRAMAN` block verifies it.


## Runtime enforcement in Python

The v0.1 runtime implements the most important cognitive wrappers as real
Python objects in `manas_sutra.runtime`. This means generated code can return a
`Verified` value instead of only a raw integer when `PHALA` declares
`Verified<T>`.

```python
from manas_sutra.runtime import Evidence

result = Evidence(value="diagnosis", confidence=0.94, threshold=0.95)
result.confidence      # 0.94
result.is_verified()   # False
result.to_proof("ISO-13485")  # raises until the confidence/proof gate passes
```

The deterministic `SumNumbers` generator now wraps `total` in `Verified` when the
`.sutra` contract declares `total: Verified<Number>`. Legacy `.msutra` examples
without cognitive output declarations still return plain Python values.
