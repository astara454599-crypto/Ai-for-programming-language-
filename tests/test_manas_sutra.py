import unittest
from pathlib import Path

from manas_sutra.compiler import compile_source
from manas_sutra.parser import ParseError, parse_source
from manas_sutra.runtime import Evidence, ProofCertificate, Unsafe, Verified


SOURCE = """
Lakshya:
    CreateTodoAPI

Dravya:
    User
    Task
    User

Bandhana:
    AuthenticationRequired
    StoreDataInDatabase

Pramana:
    UnitTests

Phala:
    FastAPIApplication
"""


class ParserTests(unittest.TestCase):
    def test_parse_source_canonicalizes_sections(self):
        program = parse_source(SOURCE)

        self.assertEqual(program.goal, "CreateTodoAPI")
        self.assertEqual(program.inputs, ("User", "Task"))
        self.assertEqual(
            program.constraints,
            ("AuthenticationRequired", "StoreDataInDatabase"),
        )
        self.assertEqual(program.outputs, ("FastAPIApplication",))

    def test_parse_formal_sutra_ai_contract(self):
        source = """
◈ TATVA [SumNumbers] {
  AGAMA {
    numbers: Evidence<List<Number>, 1.0>
  }

  BANDHANA {
    numeric_only: ENFORCE(all_numeric(numbers))
    accuracy: MANDATE(total = Σ(numbers))
  }

  JNANA {
    arithmetic: ontology://math/arithmetic
  }

  PRAMAN {
    unit: Proof<SumCorrect, "unit-test">
  }

  PHALA {
    total: Verified<Number>
  }
}
"""
        program = parse_source(source)

        self.assertEqual(program.dialect, "sutra-ai-v0.1")
        self.assertEqual(program.contract, "SumNumbers")
        self.assertEqual(program.inputs, ("numbers",))
        self.assertEqual(program.outputs, ("total",))
        self.assertIn("numeric_only: ENFORCE(all_numeric(numbers))", program.constraints)
        self.assertIn("arithmetic: ontology://math/arithmetic", program.knowledge)

    def test_parse_requires_goal(self):
        with self.assertRaises(ParseError):
            parse_source("Phala:\n    PythonModule\n")

    def test_parse_requires_output(self):
        with self.assertRaises(ParseError):
            parse_source("Lakshya:\n    BuildThing\n")



class RuntimeTypeTests(unittest.TestCase):
    def test_evidence_requires_threshold_before_proof(self):
        weak = Evidence(value="diagnosis", confidence=0.7, threshold=0.95)
        strong = Evidence(value="diagnosis", confidence=0.97, threshold=0.95)

        self.assertFalse(weak.is_verified())
        with self.assertRaises(ValueError):
            weak.to_proof("ISO-13485")
        self.assertTrue(strong.to_proof("ISO-13485").is_valid())

    def test_verified_and_unsafe_runtime_flow(self):
        proof = ProofCertificate(standard="unit-test", claims=("checked",))
        unsafe = Unsafe(value={"total": 10}, reason="missing proof")
        verified = unsafe.verify(proof)

        self.assertFalse(unsafe.is_verified())
        self.assertIsInstance(verified, Verified)
        self.assertEqual(verified.unwrap(), {"total": 10})

class CompilerTests(unittest.TestCase):
    def test_compile_builds_graph_and_python_scaffold(self):
        result = compile_source(SOURCE)

        graph = result.graph.to_dict()
        self.assertIn({"id": "goal:0", "kind": "goal", "label": "CreateTodoAPI"}, graph["nodes"])
        self.assertIn("def create_todo_api", result.python)
        self.assertIn("AuthenticationRequired", result.python)
        self.assertIn("FastAPIApplication", result.python)

    def test_sum_numbers_generator_executes_real_logic(self):
        source = """
Lakshya:
    SumNumbers

Dravya:
    numbers

Bandhana:
    AccuracyRequired
    NumericInputOnly

Pramana:
    UnitTests

Phala:
    total
"""
        result = compile_source(source)
        namespace = {}

        exec(result.python, namespace)
        execution = namespace["sum_numbers"](numbers=[1, 2, 3, 4])

        self.assertEqual(namespace["GENERATOR_KIND"], "sum_numbers")
        self.assertEqual(execution.outputs, {"total": 10})
        self.assertEqual(execution.verification_required, ("UnitTests",))

    def test_formal_sutra_ai_contract_compiles_and_executes(self):
        source = Path("examples/sutra_sum.sutra").read_text(encoding="utf-8")
        result = compile_source(source)
        namespace = {}

        exec(result.python, namespace)
        execution = namespace["sum_numbers"](numbers=[2, 4, 6])
        graph = result.graph.to_dict()

        self.assertIsInstance(execution.outputs["total"], Verified)
        self.assertEqual(execution.outputs["total"].value, 12)
        self.assertTrue(execution.outputs["total"].proof.is_valid())
        self.assertEqual(graph["dialect"], "sutra-ai-v0.1")
        self.assertIn("knowledge", {node["kind"] for node in graph["nodes"]})

    def test_rich_contract_preserves_samvad_smriti_vikasa_and_types(self):
        source = Path("examples/diagnose_disease.sutra").read_text(encoding="utf-8")
        result = compile_source(source)
        program = result.program
        graph = result.graph.to_dict()
        node_kinds = {node["kind"] for node in graph["nodes"]}

        self.assertEqual(program.contract, "DiagnoseDisease")
        self.assertIn("NidanAI", "\n".join(program.agents))
        self.assertIn("REDACT", "\n".join(program.memory))
        self.assertIn("FORBIDDEN: core_constraints.*", program.self_evolution)
        self.assertIn("Proof", program.cognitive_types)
        self.assertIn("Temporal", program.cognitive_types)
        self.assertIn("self_evolution", node_kinds)
        self.assertIn("cognitive_type", node_kinds)

    def test_render_tree_mentions_relations(self):
        result = compile_source(SOURCE)
        tree = result.graph.render_tree()

        self.assertIn("Goal: CreateTodoAPI", tree)
        self.assertIn("constraint: AuthenticationRequired [constrained_by]", tree)


if __name__ == "__main__":
    unittest.main()
