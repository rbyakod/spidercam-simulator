from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from controllers.sim_controller import SimController
from executor import MotionExecutor
from machine_state import default_state, refresh_state
from models import build_runtime_context
from persistent_config import DEFAULT_CONFIG


class MotionExecutorTests(unittest.TestCase):
    def setUp(self) -> None:
        config = DEFAULT_CONFIG.model_copy(deep=True)
        self.context = build_runtime_context(config)
        self.executor = MotionExecutor(self.context, SimController(self.context))
        self.state = default_state(self.context)

    def test_default_state_contains_v15_runtime_fields(self):
        self.assertIn("armed", self.state)
        self.assertIn("controller_ready", self.state)
        self.assertIn("geometry_valid", self.state)
        self.assertIn("calibration_valid", self.state)
        self.assertIn("faults", self.state)
        self.assertIn("warnings", self.state)
        self.assertIn("homed", self.state)
        self.assertFalse(self.state["calibration_valid"])

    def test_set_target_accepts_valid_target_and_sets_target_lengths(self):
        result = self.executor.set_target(self.state, 1.2, 1.0, 0.9, 0.6)
        self.assertTrue(result["ok"])
        self.assertAlmostEqual(self.state["target"]["x"], 1.2)
        self.assertEqual(self.state["status"], "moving")
        self.assertIn("A", self.state["target_lengths"])

    def test_set_target_rejects_invalid_target_without_clamping(self):
        result = self.executor.set_target(self.state, 10.0, -5.0, 99.0, 0.6)
        self.assertFalse(result["ok"])
        self.assertIsNotNone(self.state["last_error"])
        self.assertEqual(self.state["target"], self.state["position"])

    def test_estop_refreshes_to_estopped_status(self):
        self.executor.estop(self.state)
        refreshed = refresh_state(self.state, self.context)
        self.assertTrue(refreshed["estop"])
        self.assertEqual(refreshed["status"], "estopped")

    def test_advance_state_moves_pose_and_appends_trail(self):
        self.executor.set_target(self.state, 1.2, 1.0, 0.9, 0.6)
        before_x = self.state["position"]["x"]
        self.executor.advance_state(self.state, 1 / 60)
        self.assertGreater(self.state["position"]["x"], before_x)
        self.assertEqual(len(self.state["trail"]), 1)
        self.assertNotEqual(self.state["lengths"], self.state["target_lengths"])


if __name__ == "__main__":
    unittest.main()
