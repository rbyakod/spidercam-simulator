from __future__ import annotations

import sys
import unittest
from math import sqrt
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from kinematics import lengths_from_xyz, steps_from_delta_length
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


if __name__ == "__main__":
    unittest.main()
