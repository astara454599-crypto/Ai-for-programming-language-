import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from manas_sutra.viveka import VivekaEngine, VivekaError, build_viveka_spec


class FakeCompletions:
    def __init__(self, response_text):
        self.response_text = response_text
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=self.response_text)
                )
            ]
        )


class FakeClient:
    def __init__(self, response_text):
        self.chat = SimpleNamespace(
            completions=FakeCompletions(response_text)
        )


class VivekaTests(unittest.TestCase):
    @patch("manas_sutra.viveka._post_safety_check", return_value={"approved": True})
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    def test_synthesize_returns_valid_python_from_mocked_api(self, safety_check):
        code = """
from manas_sutra.runtime import ProofCertificate, Verified


def sum_numbers(**inputs):
    total = sum(inputs["numbers"])
    proof = ProofCertificate(standard="mock", claims=("summed",))
    return {"total": Verified(total, proof)}
"""
        client = FakeClient(f"```python\n{code}\n```")
        engine = VivekaEngine(client=client)
        spec = build_viveka_spec(
            Path("examples/sutra_sum.sutra").read_text(encoding="utf-8")
        )

        synthesized = engine.synthesize(spec)
        kwargs = client.chat.completions.last_kwargs

        self.assertIn("def sum_numbers", synthesized)
        compile(synthesized, "<test-viveka>", "exec")
        self.assertEqual(kwargs["model"], "mistralai/mistral-7b-instruct")
        self.assertEqual(kwargs["messages"][0]["role"], "system")
        self.assertIn("SUTRA-AI", kwargs["messages"][0]["content"])
        self.assertEqual(kwargs["messages"][1]["role"], "user")
        self.assertIn("Verified", kwargs["messages"][1]["content"])
        safety_check.assert_called_once()

    @patch("manas_sutra.viveka._post_safety_check", return_value={"approved": True})
    def test_synthesize_rejects_invalid_python(self, safety_check):
        engine = VivekaEngine(client=FakeClient("not valid python !!!"))

        with self.assertRaises(VivekaError):
            engine.synthesize({"program": {"goal": "Broken"}})
        safety_check.assert_called_once()

    @patch("manas_sutra.viveka._post_safety_check", return_value={"approved": False, "reason": "Rejected by safety policy."})
    def test_synthesize_stops_when_safety_rejects(self, safety_check):
        engine = VivekaEngine(client=FakeClient("def should_not_run(): pass"))

        with self.assertRaisesRegex(VivekaError, "Rejected by safety policy"):
            engine.synthesize({"program": {"goal": "Blocked"}})
        self.assertIsNone(engine.client.chat.completions.last_kwargs)

    @patch("manas_sutra.viveka._post_safety_check", side_effect=VivekaError("Safety server not running. Start it before synthesizing."))
    def test_synthesize_requires_running_safety_server(self, safety_check):
        engine = VivekaEngine(client=FakeClient("def should_not_run(): pass"))

        with self.assertRaisesRegex(VivekaError, "Safety server not running"):
            engine.synthesize({"program": {"goal": "NoServer"}})
        self.assertIsNone(engine.client.chat.completions.last_kwargs)

    @patch.dict(os.environ, {}, clear=True)
    def test_build_client_requires_openrouter_key(self):
        with self.assertRaisesRegex(VivekaError, "OPENROUTER_API_KEY"):
            VivekaEngine()._build_client()


if __name__ == "__main__":
    unittest.main()
