"""Runtime cognitive types for SUTRA-AI generated artifacts.

These classes turn declarations such as ``Evidence<T, p>`` and
``Verified<T>`` from passive parser metadata into enforceable Python objects.
They are intentionally small and deterministic in v0.1; formal proof engines
can later replace the local ``ProofCertificate`` checks without changing the
public runtime shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable


@dataclass(frozen=True)
class ProofCertificate:
    """A machine-checkable proof placeholder attached to verified values."""

    standard: str
    claims: tuple[str, ...]
    checker: str = "sutra-ai-runtime-v0.1"
    machine_checkable: bool = True

    def is_valid(self) -> bool:
        """Return whether the proof can be accepted by the local runtime."""

        return self.machine_checkable and bool(self.standard) and bool(self.claims)


@dataclass(frozen=True)
class Evidence:
    """A value with an epistemic confidence score."""

    value: Any
    confidence: float
    source: str | None = None
    threshold: float = 0.95

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("Evidence confidence must be in [0, 1].")
        if not 0 <= self.threshold <= 1:
            raise ValueError("Evidence threshold must be in [0, 1].")

    def is_verified(self) -> bool:
        """Return true when confidence reaches the required threshold."""

        return self.confidence >= self.threshold

    def to_proof(self, standard: str) -> ProofCertificate:
        """Create a proof certificate if evidence passes its threshold."""

        if not self.is_verified():
            raise ValueError(
                f"Evidence confidence {self.confidence} is below threshold {self.threshold}."
            )
        return ProofCertificate(
            standard=standard,
            claims=(f"confidence>={self.threshold}", f"value={self.value!r}"),
        )


@dataclass(frozen=True)
class Verified:
    """A value that carries a valid proof certificate."""

    value: Any
    proof: ProofCertificate

    def __post_init__(self) -> None:
        if not self.proof.is_valid():
            raise ValueError("Verified values require a valid proof certificate.")

    def is_verified(self) -> bool:
        return True

    def unwrap(self) -> Any:
        return self.value


@dataclass(frozen=True)
class Unsafe:
    """A value that must not be consumed until a proof verifies it."""

    value: Any
    reason: str

    def is_verified(self) -> bool:
        return False

    def verify(self, proof: ProofCertificate) -> Verified:
        return Verified(value=self.value, proof=proof)


@dataclass(frozen=True)
class Uncertain:
    """A value with uncertainty spread sigma."""

    value: Any
    sigma: float

    def __post_init__(self) -> None:
        if self.sigma < 0:
            raise ValueError("Uncertainty sigma must be non-negative.")


@dataclass(frozen=True)
class Causal:
    """A causal relationship with strength in [0, 1]."""

    cause: Any
    effect: Any
    strength: float

    def __post_init__(self) -> None:
        if not 0 <= self.strength <= 1:
            raise ValueError("Causal strength must be in [0, 1].")


@dataclass(frozen=True)
class Temporal:
    """A value that is valid until an optional expiration time."""

    value: Any
    valid_until: datetime | None = None
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_valid(self, now: datetime | None = None) -> bool:
        if self.valid_until is None:
            return True
        current = now or datetime.now(timezone.utc)
        return current <= self.valid_until


@dataclass(frozen=True)
class Contested:
    """A value with unresolved conflicting evidence."""

    value: Any
    conflicts: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.conflicts:
            raise ValueError("Contested values must include at least one conflict.")

    def is_verified(self) -> bool:
        return False


@dataclass(frozen=True)
class Redacted:
    """A differentially private or policy-redacted value."""

    value: Any
    epsilon: float
    delta: float = 0.0
    redactions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.epsilon <= 0:
            raise ValueError("Redacted epsilon must be positive.")
        if self.delta < 0:
            raise ValueError("Redacted delta must be non-negative.")


@dataclass(frozen=True)
class Goal:
    """A verifiable objective targeting an outcome."""

    name: str
    constraints: tuple[str, ...] = ()


def require_verified(values: Iterable[Any]) -> None:
    """Raise if any value is explicitly unsafe or unverified evidence."""

    for value in values:
        if isinstance(value, Unsafe):
            raise ValueError(f"Unsafe value blocked: {value.reason}")
        if isinstance(value, Evidence) and not value.is_verified():
            raise ValueError("Evidence value is below its verification threshold.")
        if isinstance(value, Contested):
            raise ValueError("Contested value must be resolved before use.")
