import unittest
from backend.core.risk_scoring_simple import (
    DetectedObject, assess, prioritize, AlertManager)


class TestRisk(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(assess(DetectedObject("pedestrian", 8)).level, "LOW")
        self.assertEqual(assess(DetectedObject("car", 5)).level, "MEDIUM")
        self.assertEqual(assess(DetectedObject("bike", 2)).level, "HIGH")

    def test_most_dangerous_first(self):
        objs = [DetectedObject("pedestrian", 8), DetectedObject("bike", 2)]
        self.assertEqual(prioritize(objs)[0].obj.kind, "bike")

    def test_only_one_alert(self):
        objs = [DetectedObject("car", 5), DetectedObject("bike", 2)]
        self.assertIn("bike", AlertManager().next_alert(objs))


if _name_ == "_main_":
    unittest.main()
