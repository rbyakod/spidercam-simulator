from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from controllers.controller_manager import ControllerManager
from controllers.dry_run_controller import DryRunController
from controllers.hardware_controller import HardwareController
from controllers.sim_controller import SimController
from executor import MotionExecutor
from machine_state import default_state, refresh_state
from models import build_runtime_context
from persistent_config import DEFAULT_CONFIG


class MotionExecutorTests(unittest.TestCase):
    def setUp(self) -> None:
        config = DEFAULT_CONFIG.model_copy(deep=True)
        self.context = build_runtime_context(config)
        self.executor = MotionExecutor(
            self.context,
            ControllerManager(
                {
                    "sim": SimController(self.context),
                    "dry_run": DryRunController(self.context),
                    "hardware": HardwareController(self.context),
                }
            ),
        )
        self.state = default_state(self.context)
        self.executor.sync_state(self.state)

    def test_default_state_is_sim_ready_for_browser_use(self):
        self.assertEqual(self.state["mode"], "sim")
        self.assertTrue(self.state["armed"])
        self.assertTrue(self.state["controller_ready"])
        self.assertTrue(self.state["calibration_valid"])
        self.assertTrue(all(self.state["homed"].values()))
        self.assertTrue(self.state["limits_verified"])

    def test_set_target_accepts_valid_target_and_sets_target_lengths(self):
        result = self.executor.set_target(self.state, 1.2, 1.0, 0.9, 0.6)
        self.assertTrue(result["ok"])
        self.assertAlmostEqual(self.state["target"]["x"], 1.2)
        self.assertEqual(self.state["status"], "moving")
        self.assertIn("A", self.state["target_lengths"])

    def test_disarm_blocks_motion_until_arm(self):
        self.executor.disarm(self.state)
        blocked = self.executor.set_target(self.state, 1.2, 1.0, 0.9, 0.6)
        self.assertFalse(blocked["ok"])
        self.executor.arm(self.state)
        allowed = self.executor.set_target(self.state, 1.2, 1.0, 0.9, 0.6)
        self.assertTrue(allowed["ok"])

    def test_hardware_mode_blocks_motion_when_controller_not_ready(self):
        self.executor.set_mode(self.state, "hardware")
        result = self.executor.set_target(self.state, 1.2, 1.0, 0.9, 0.6)
        self.assertFalse(result["ok"])
        self.assertFalse(self.state["controller_ready"])
        self.assertIn("hardware_controller_unavailable_in_starter", self.state["last_error"])

    def test_dry_run_home_and_calibration_generate_trace(self):
        self.executor.set_mode(self.state, "dry_run")
        self.state["homed"] = {name: False for name in self.context.cable_names}
        self.state["limits_verified"] = False
        self.state["motor_direction_ok"] = {name: False for name in self.context.cable_names}

        self.assertTrue(self.executor.home(self.state)["ok"])
        self.assertTrue(self.executor.verify_limits(self.state)["ok"])
        self.assertTrue(self.executor.verify_motor_directions(self.state)["ok"])
        self.assertTrue(self.executor.calibrate(self.state)["ok"])

        refreshed = refresh_state(self.state, self.context)
        self.assertTrue(refreshed["calibration_valid"])
        self.assertTrue(refreshed["controller_trace"])

    def test_advance_state_moves_pose_and_appends_trail(self):
        self.executor.set_target(self.state, 1.2, 1.0, 0.9, 0.6)
        before_x = self.state["position"]["x"]
        self.executor.advance_state(self.state, 1 / 60)
        self.assertGreater(self.state["position"]["x"], before_x)
        self.assertEqual(len(self.state["trail"]), 1)
        self.assertNotEqual(self.state["lengths"], self.state["target_lengths"])


if __name__ == "__main__":
    unittest.main()
