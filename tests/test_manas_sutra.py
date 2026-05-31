import unittest

from manas_sutra.compiler import compile_source
from manas_sutra.parser import ParseError, parse_source


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

    def test_parse_requires_goal(self):
        with self.assertRaises(ParseError):
            parse_source("Phala:\n    PythonModule\n")

    def test_parse_requires_output(self):
        with self.assertRaises(ParseError):
            parse_source("Lakshya:\n    BuildThing\n")


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

    def test_render_tree_mentions_relations(self):
        result = compile_source(SOURCE)
        tree = result.graph.render_tree()

        self.assertIn("Goal: CreateTodoAPI", tree)
        self.assertIn("constraint: AuthenticationRequired [constrained_by]", tree)


if __name__ == "__main__":
    unittest.main()
