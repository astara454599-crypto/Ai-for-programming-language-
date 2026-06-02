"""VIVEKA reasoning engine for LLM-assisted SUTRA-AI synthesis.

VIVEKA is the reasoning/synthesis layer. It receives a canonical SUTRA-AI
contract or JALA graph dictionary, sends it to OpenRouter, and expects back only
valid Python implementation code that can use the local cognitive runtime types.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .compiler import compile_source
from .parser import ParseError

DEFAULT_MODEL = "mistralai/mistral-7b-instruct"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
SAFETY_CHECK_URL = "http://localhost:8000/safety/check"

SYSTEM_PROMPT = """You are the VIVEKA layer of SUTRA-AI.
You are a Python implementation synthesizer for AI-native cognitive contracts.
You receive a structured SUTRA-AI specification containing AGAMA inputs,
BANDHANA constraints, JNANA knowledge references, ANVESHANA search directives,
PRAMAN proof requirements, SAMVAD agent requirements, SMRITI memory, and PHALA
outputs.

Return ONLY valid Python code. Do not include markdown fences or explanation.
The code must define one Python function matching the contract goal, accept
inputs by keyword arguments, and return a dictionary or an ExecutionResult-like
object. Use manas_sutra.runtime cognitive types where the PHALA declarations
require them: Evidence, ProofCertificate, Verified, Unsafe, Uncertain, Causal,
Temporal, Contested, Redacted, Goal, and require_verified. Preserve constraints
as runtime checks where practical. If a proof cannot be machine-checked, return
Unsafe rather than pretending it is Verified.
"""


class VivekaError(RuntimeError):
    """Raised when VIVEKA synthesis cannot complete safely."""


@dataclass(frozen=True)
class VivekaEngine:
    """OpenRouter-backed implementation synthesizer for SUTRA-AI contracts."""

    api_key: str | None = None
    model: str = DEFAULT_MODEL
    client: Any | None = None
    max_tokens: int = 4000
    safety_url: str = SAFETY_CHECK_URL

    def synthesize(self, tatva_spec: dict[str, Any]) -> str:
        """Synthesize Python code for a canonical SUTRA-AI/JALA specification."""

        self._check_safety(tatva_spec)
        client = self.client or self._build_client()
        user_prompt = self._build_user_prompt(tatva_spec)

        try:
            response = client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as exc:
            raise VivekaError(f"VIVEKA synthesis API call failed: {exc}") from exc

        code = _strip_markdown_fences(_response_text(response)).strip()
        if not code:
            raise VivekaError("VIVEKA synthesis returned empty code.")

        try:
            compile(code, "<viveka-synthesis>", "exec")
        except SyntaxError as exc:
            raise VivekaError(f"VIVEKA synthesis returned invalid Python: {exc}") from exc

        return code

    def _check_safety(self, tatva_spec: dict[str, Any]) -> None:
        result = _post_safety_check(tatva_spec, self.safety_url)
        if result.get("approved") is not True:
            reason = result.get("reason") or "Safety check rejected the specification."
            raise VivekaError(str(reason))

    def _build_client(self) -> Any:
        api_key = self.api_key or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise VivekaError("OPENROUTER_API_KEY is required for VIVEKA synthesis.")
        if importlib.util.find_spec("openai") is None:
            raise VivekaError(
                "The 'openai' package is required. Install dependencies with "
                "`python -m pip install -r requirements.txt`."
            )

        from openai import OpenAI

        return OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=api_key,
        )

    def _build_user_prompt(self, tatva_spec: dict[str, Any]) -> str:
        encoded = json.dumps(tatva_spec, indent=2, sort_keys=True, ensure_ascii=False)
        return f"""Synthesize a Python implementation for this SUTRA-AI contract.

Rules:
1. Return only Python code.
2. Define a function whose name is the snake_case form of the contract/goal.
3. Accept AGAMA inputs as keyword arguments or explicit parameters.
4. Enforce BANDHANA constraints with runtime checks where practical.
5. Use manas_sutra.runtime types for PHALA declarations such as Verified<T>,
   Evidence<T,p>, Uncertain<T,σ>, Causal<A→B,γ>, Temporal<T,Δt>, and Unsafe<T>.
6. Do not claim formal proof if the specification does not provide one; return
   Unsafe or a ProofCertificate with clear local claims instead.

SPECIFICATION_JSON:
{encoded}
"""


def _post_safety_check(tatva_spec: dict[str, Any], safety_url: str) -> dict[str, Any]:
    payload = json.dumps(tatva_spec).encode("utf-8")
    request = urllib.request.Request(
        safety_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise VivekaError(
            "Safety server not running. Start it before synthesizing."
        ) from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise VivekaError("Safety server returned invalid JSON.") from exc
    if not isinstance(parsed, dict):
        raise VivekaError("Safety server returned an invalid response.")
    return parsed


def _response_text(response: Any) -> str:
    return response.choices[0].message.content or ""


def _strip_markdown_fences(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped

    lines = stripped.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)


def build_viveka_spec(source: str) -> dict[str, Any]:
    """Compile source into the structured dict sent to the VIVEKA layer."""

    result = compile_source(source)
    return {
        "program": result.program.to_dict(),
        "graph": result.graph.to_dict(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run VIVEKA LLM synthesis for a .sutra file.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--out", type=Path, help="Write synthesized Python to this file.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenRouter model name.")
    parser.add_argument(
        "--print-spec",
        action="store_true",
        help="Print the structured VIVEKA input JSON instead of calling the API.",
    )
    args = parser.parse_args()

    try:
        spec = build_viveka_spec(args.source.read_text(encoding="utf-8"))
        if args.print_spec:
            print(json.dumps(spec, indent=2, ensure_ascii=False))
            return 0
        code = VivekaEngine(model=args.model).synthesize(spec)
    except (OSError, ParseError, VivekaError) as exc:
        parser.error(str(exc))
        return 2

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(code, encoding="utf-8")
    else:
        print(code)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
