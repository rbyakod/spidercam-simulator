from __future__ import annotations

import sys
import unittest
from math import sqrt
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from kinematics import lengths_from_xyz, solve_position_from_lengths, steps_from_delta_length
from models import build_runtime_context
from persistent_config import DEFAULT_CONFIG


class KinematicsTests(unittest.TestCase):
    def setUp(self) -> None:
        config = DEFAULT_CONFIG.model_copy(deep=True)
        self.context = build_runtime_context(config)

    def test_center_lengths_are_symmetric(self):
        lengths = lengths_from_xyz(self.context.anchors, 1.0, 1.0, 0.9)
        expected = sqrt((1.0 - 0.0) ** 2 + (1.0 - 0.0) ** 2 + (0.9 - 1.5) ** 2)
        self.assertAlmostEqual(lengths["A"], expected, places=6)
        self.assertAlmostEqual(lengths["A"], lengths["B"], places=6)
        self.assertAlmostEqual(lengths["A"], lengths["C"], places=6)
        self.assertAlmostEqual(lengths["A"], lengths["D"], places=6)

    def test_steps_match_one_spool_revolution(self):
        circumference = 2 * 3.141592653589793 * self.context.spool_radius_m
        steps = steps_from_delta_length(circumference, self.context)
        self.assertEqual(steps, self.context.motor_steps_per_rev * self.context.microsteps)

    def test_lengths_round_trip_back_to_position(self):
        original = {"x": 1.27, "y": 0.84, "z": 0.73}
        lengths = lengths_from_xyz(self.context.anchors, **original)
        solved = solve_position_from_lengths(self.context, lengths, initial_guess={"x": 1.0, "y": 1.0, "z": 0.9})
        self.assertTrue(solved["success"])
        self.assertAlmostEqual(solved["position"]["x"], original["x"], places=5)
        self.assertAlmostEqual(solved["position"]["y"], original["y"], places=5)
        self.assertAlmostEqual(solved["position"]["z"], original["z"], places=5)


if __name__ == "__main__":
    unittest.main()
