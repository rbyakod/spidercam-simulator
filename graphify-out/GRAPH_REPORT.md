# Graph Report - SpiderCam  (2026-08-22)

## Corpus Check
- 162 files · ~101,054 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1164 nodes · 1907 edges · 84 communities (67 shown, 17 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 132 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `72dcfa9e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- RuntimeContext
- spiderpi-sim-starter/backend/main.py
- spiderpi-sim-starter/frontend/src/components/SpiderScene.tsx
- spiderpi-sim-starter/frontend/package.json
- final/frontend/src/App.tsx
- compilerOptions
- MotionExecutor
- from-cowork-original/frontend/src/App.tsx
- create_spiderpi_sim.sh
- __init__.py
- devDependencies
- from-cowork-original/backend/main.py
- HardwareRuntime
- SpiderPi System Runbook
- MotionBackend
- from-cowork-original/frontend/package.json
- compilerOptions
- compilerOptions
- load_config
- SpiderPi Hardware Build Guide
- MotionProfile
- final/backend/main.py
- SpiderCAM Runbook - How to Compile and Run All Services
- set_target
- FaultCode
- GPIORuntime
- RampedScheduler
- SpiderPi Calibration Checklist
- v0.1-desktop (1m x 1m desktop prototype)
- MultiAxisRampScheduler
- HomingMonitor
- SpiderPi Multi-Axis Test Sequences
- from-cowork-original/backend/profile_store.py
- SpiderPi Real Hardware Bring-up Guide
- MotionBackend
- ProfileStore
- SpiderCAM Real Hardware Bring-Up Guide
- from-cowork-original/backend/calibration_state.py
- FaultManager
- GPIOMotionBackend
- from-cowork-original/backend/path_store.py
- SpiderPi Calibration Troubleshooting Guide
- SpiderPi Mechanical Drawings Reference
- PathStore
- SimExecutor
- SpiderCAM Build Guide
- SpiderCAM Calibration Checklist
- SpiderCAM Multi-Axis Test Sequences
- GPIORuntime
- motor_metrics
- SimMotionBackend
- SpiderPi Spool Design Specification
- load_gpio_map
- HomingController
- SpiderCAM Calibration Troubleshooting
- SpiderCAM Manufacturing Release Checklist
- LimitMonitor
- from-cowork-original/backend/persistent_config.py
- SafeMotionController
- SpiderPi CAD Package - Ready to Print
- SpiderPi Wiring Diagram - Desktop 1m Profile
- Hardware Gate Integration Guide
- SpiderPi - Cable Robot Simulator and Controller
- CalibrationStep
- SpiderCAM Bill of Materials - Regional Notes
- SpiderCAM Desktop 1m Frame - Wiring Diagram
- SpiderCAM Mechanical Drawings and Dimensions
- SpiderCAM - Raspberry Pi Cable Robot Camera System
- SpiderCAM Spool Design Specification
- Manager
- SpiderPi Wiring Table
- SpiderCAM CAD Drawings Status
- SpiderCAM Hardware Gate Integration
- SpiderCAM GPIO Wiring Table
- HomingController
- SpiderPi Regional Bill of Materials

## God Nodes (most connected - your core abstractions)
1. `MotionExecutor` - 29 edges
2. `RuntimeContext` - 27 edges
3. `HardwareRuntime` - 24 edges
4. `FaultManager` - 21 edges
5. `HardwareExecutor` - 21 edges
6. `refresh_state()` - 21 edges
7. `SystemConfig` - 20 edges
8. `HomingMonitor` - 18 edges
9. `load_config()` - 18 edges
10. `BaseController` - 18 edges

## Surprising Connections (you probably didn't know these)
- `CalibrateRequest` --uses--> `CalibrationStep`  [INFERRED]
  docs/perplexity-design/final/backend/main.py → docs/perplexity-design/final/backend/calibration_state.py
- `ConnectionManager` --uses--> `CalibrationStep`  [INFERRED]
  docs/perplexity-design/final/backend/main.py → docs/perplexity-design/final/backend/calibration_state.py
- `JogRequest` --uses--> `CalibrationStep`  [INFERRED]
  docs/perplexity-design/final/backend/main.py → docs/perplexity-design/final/backend/calibration_state.py
- `MoveRequest` --uses--> `CalibrationStep`  [INFERRED]
  docs/perplexity-design/final/backend/main.py → docs/perplexity-design/final/backend/calibration_state.py
- `PathRequest` --uses--> `CalibrationStep`  [INFERRED]
  docs/perplexity-design/final/backend/main.py → docs/perplexity-design/final/backend/calibration_state.py

## Import Cycles
- None detected.

## Communities (84 total, 17 thin omitted)

### Community 0 - "RuntimeContext"
Cohesion: 0.06
Nodes (41): Path, BaseController, ControllerManager, DryRunController, HardwareController, SimController, lengths_from_position(), lengths_from_xyz() (+33 more)

### Community 1 - "spiderpi-sim-starter/backend/main.py"
Cohesion: 0.13
Nodes (32): get, post, arm(), calibrate(), current_state(), disarm(), estop(), get_state() (+24 more)

### Community 2 - "spiderpi-sim-starter/frontend/src/components/SpiderScene.tsx"
Cohesion: 0.08
Nodes (23): App(), Controls(), clamp(), DEFAULTS, FramePlanner(), num(), plannerFromState(), PlannerInputs (+15 more)

### Community 3 - "spiderpi-sim-starter/frontend/package.json"
Cohesion: 0.06
Nodes (32): react, react-dom, @react-three/drei, @react-three/fiber, dependencies, react, react-dom, @react-three/drei (+24 more)

### Community 4 - "final/frontend/src/App.tsx"
Cohesion: 0.06
Nodes (38): App(), CalibrationPanel(), CalibrationWizard(), STEPS, Controls(), DEFAULT_FRAME, validateFrame(), FrameSizingPanel() (+30 more)

### Community 5 - "compilerOptions"
Cohesion: 0.10
Nodes (20): DOM, DOM.Iterable, ES2020, src, compilerOptions, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames (+12 more)

### Community 7 - "from-cowork-original/frontend/src/App.tsx"
Cohesion: 0.07
Nodes (24): App(), CalibrationPanel(), CalibrationWizard(), Controls(), DEFAULTS, FrameSizingPanel(), HardwareGatePanel(), HomingPanel() (+16 more)

### Community 11 - "devDependencies"
Cohesion: 0.05
Nodes (42): axios, dependencies, axios, react, react-dom, @react-three/drei, @react-three/fiber, three (+34 more)

### Community 12 - "from-cowork-original/backend/main.py"
Cohesion: 0.10
Nodes (39): compute_gates(), step_gate_status(), anchors(), apply_position(), cfg(), estop(), faults(), get_config() (+31 more)

### Community 13 - "HardwareRuntime"
Cohesion: 0.15
Nodes (20): FaultManager, HomingMonitor, HardwareExecutor, HardwareRuntime, BoundsCmd, ConfigUpdateCmd, DirectionCmd, HomeCmd (+12 more)

### Community 14 - "SpiderPi System Runbook"
Cohesion: 0.05
Nodes (37): API Reference, Common Workflows, Directory Structure, Environment variables (optional), File Locations, macOS (simulation mode), Monitoring, Prerequisites (+29 more)

### Community 15 - "MotionBackend"
Cohesion: 0.09
Nodes (17): BaseSettings, CalibrationManager, ndarray, Config, Settings, steps_per_metre(), MotionBackend, anchors() (+9 more)

### Community 16 - "from-cowork-original/frontend/package.json"
Cohesion: 0.06
Nodes (32): dependencies, react, react-dom, @react-three/drei, @react-three/fiber, three, devDependencies, @types/react (+24 more)

### Community 17 - "compilerOptions"
Cohesion: 0.09
Nodes (22): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+14 more)

### Community 18 - "compilerOptions"
Cohesion: 0.09
Nodes (22): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+14 more)

### Community 19 - "load_config"
Cohesion: 0.25
Nodes (19): current_step(), get_wizard_state(), set_bounds(), set_homed(), set_line_offsets(), set_motor_direction(), set_spool_radius(), set_zero_lengths() (+11 more)

### Community 20 - "SpiderPi Hardware Build Guide"
Cohesion: 0.10
Nodes (19): Architecture, DRV8825 Current Limit Setting, DRV8825 wiring (per motor), Electronics Wiring, Frame Assembly, GPIO pin assignment, Limit switch wiring, Power architecture (+11 more)

### Community 21 - "MotionProfile"
Cohesion: 0.16
Nodes (17): api_calibrate(), api_estop(), api_fault_clear(), api_home(), api_jog(), api_move(), CalibrateRequest, JogRequest (+9 more)

### Community 22 - "final/backend/main.py"
Cohesion: 0.20
Nodes (14): hardware_loop(), api_calibrate_status(), api_home_status(), api_status(), delete_path(), delete_profile(), get_gpio(), health() (+6 more)

### Community 23 - "SpiderCAM Runbook - How to Compile and Run All Services"
Cohesion: 0.12
Nodes (15): 1. Start Backend, 2. Start Frontend (new terminal), 3. Verify, API Endpoints Reference, Environment Variables, Export STL from CAD, Generate GPIO Map, Option A: Development Mode (Simulator) (+7 more)

### Community 24 - "set_target"
Cohesion: 0.26
Nodes (14): bounds(), clamp(), move(), run_path(), set_path(), set_target(), stop(), websocket_endpoint() (+6 more)

### Community 25 - "FaultCode"
Cohesion: 0.18
Nodes (5): FaultCode, FaultEvent, Enum, str, LimitMonitor

### Community 27 - "RampedScheduler"
Cohesion: 0.21
Nodes (4): ConnectionManager, WebSocket, ws_telemetry(), RampedScheduler

### Community 28 - "SpiderPi Calibration Checklist"
Cohesion: 0.17
Nodes (11): 10. Acceptance, 1. Frame Sizing and Profile, 2. Visual Geometry Check, 3. Wiring and I/O Check, 4. Motor Direction Verification, 5. Homing All Axes, 6. Spool Radius Calibration, 7. Center and Zero Calibration (+3 more)

### Community 29 - "v0.1-desktop (1m x 1m desktop prototype)"
Cohesion: 0.17
Nodes (11): Acceptance Test, Documentation, Electronics, Frame, Frame, Performance, Software, SpiderPi Manufacturing Release Checklist (+3 more)

### Community 30 - "MultiAxisRampScheduler"
Cohesion: 0.27
Nodes (3): dda_sync_plan(), trapezoid_profile(), MultiAxisRampScheduler

### Community 32 - "SpiderPi Multi-Axis Test Sequences"
Cohesion: 0.18
Nodes (10): SpiderPi Multi-Axis Test Sequences, Test 1: Single Axis Sanity (run per axis, one at a time), Test 2: Opposite Pair Symmetry, Test 3: Z Collective Move, Test 4: Micro-Square Path, Test 5: Micro-Circle Path, Test 6: Diagonal Sweep, Test 7: Repeatability Test (+2 more)

### Community 33 - "from-cowork-original/backend/profile_store.py"
Cohesion: 0.36
Nodes (8): get_profiles(), _atomic_write(), delete_profile(), get_profile(), list_profiles(), load_profiles(), Path, save_profile()

### Community 34 - "SpiderPi Real Hardware Bring-up Guide"
Cohesion: 0.20
Nodes (9): Prerequisites, SpiderPi Real Hardware Bring-up Guide, Stage 1: Pi Setup, Stage 2: Deploy Backend, Stage 3: Verify API from MacBook, Stage 4: Enable Real GPIO, Stage 5: Staged Motor Testing, Stage 6: Calibration Sequence (+1 more)

### Community 37 - "SpiderCAM Real Hardware Bring-Up Guide"
Cohesion: 0.22
Nodes (8): Common Issues, SpiderCAM Real Hardware Bring-Up Guide, Step 1: Set DRV8825 Current Limits, Step 2: Single Axis Motor Test, Step 3: Limit Switch Test, Step 4: First Homing Run, Step 5: First Move, Step 6: Calibration

### Community 38 - "from-cowork-original/backend/calibration_state.py"
Cohesion: 0.42
Nodes (8): _atomic_write(), _default_wizard(), get_wizard_with_checklist(), load_wizard(), mark_step(), Path, reset_wizard(), save_wizard()

### Community 40 - "GPIOMotionBackend"
Cohesion: 0.25
Nodes (3): GPIOMotionBackend, MotionBackend, build_backend()

### Community 41 - "from-cowork-original/backend/path_store.py"
Cohesion: 0.47
Nodes (8): _atomic_write(), delete_path(), list_paths(), load_paths(), Path, save_paths(), upsert_path(), upsert_pose()

### Community 42 - "SpiderPi Calibration Troubleshooting Guide"
Cohesion: 0.22
Nodes (8): Cable Problems, Dashboard/WebSocket Problems, Homing Problems, Motor Direction Problems, Motor Overload Warnings, Position Accuracy Problems, SpiderPi Calibration Troubleshooting Guide, Spool Radius Problems

### Community 43 - "SpiderPi Mechanical Drawings Reference"
Cohesion: 0.22
Nodes (8): Carriage Plate, Coordinate System, Fabrication Tolerances, Frame Members (2020 extrusion), room_2m Profile Dimensions, SpiderPi Mechanical Drawings Reference, Spool Design Parameters, Verification Procedure

### Community 46 - "SpiderCAM Build Guide"
Cohesion: 0.25
Nodes (7): 1. Frame Assembly, 2. Motor Mounting, 3. Spool Installation, 4. Cable Rigging, 5. Electronics Assembly, 6. Software Installation, SpiderCAM Build Guide

### Community 47 - "SpiderCAM Calibration Checklist"
Cohesion: 0.25
Nodes (7): Pre-Calibration Checks, SpiderCAM Calibration Checklist, Step 1: Homing, Step 2: Move to Reference Position, Step 3: Measure Cable Lengths, Step 4: Enter Measurements, Step 5: Verify

### Community 48 - "SpiderCAM Multi-Axis Test Sequences"
Cohesion: 0.25
Nodes (7): SpiderCAM Multi-Axis Test Sequences, Test 1: Single-Axis Jog Verification, Test 2: Square Path, Test 3: Diagonal Speed Test, Test 4: Extreme Position Stress Test, Test 5: Endurance Run (30 minutes), Test 6: Emergency Stop Recovery

### Community 50 - "motor_metrics"
Cohesion: 0.54
Nodes (7): available_torque_nm(), drv8825_current_limit(), line_pull_capacity_n(), motor_metrics(), solve_tensions(), unit_vec(), vec_len()

### Community 52 - "SpiderPi Spool Design Specification"
Cohesion: 0.25
Nodes (7): Baseline Design, Critical Parameter: Effective Spool Radius, Fit Tolerances, Material Recommendations, NEMA17 Shaft Compatibility, Print Settings, SpiderPi Spool Design Specification

### Community 53 - "load_gpio_map"
Cohesion: 0.33
Nodes (4): load_gpio_map(), save_gpio_map(), set_gpio(), create_executor()

### Community 55 - "SpiderCAM Calibration Troubleshooting"
Cohesion: 0.29
Nodes (6): Problem: Accuracy degrades over time, Problem: Calibration says OK but position is wrong, Problem: Homing fails on one axis, Problem: Offsets are very large (>100mm), Problem: One cable always reads zero tension, SpiderCAM Calibration Troubleshooting

### Community 56 - "SpiderCAM Manufacturing Release Checklist"
Cohesion: 0.29
Nodes (6): Bill of Materials, CAD Files, Sign-Off, Software, SpiderCAM Manufacturing Release Checklist, Test Results

### Community 58 - "from-cowork-original/backend/persistent_config.py"
Cohesion: 0.48
Nodes (6): CalibrationState, FrameConfig, MotorPinConfig, MotorTuning, BaseModel, RigConfig

### Community 60 - "SpiderPi CAD Package - Ready to Print"
Cohesion: 0.29
Nodes (6): Critical Dimension Verification, Exporting to STEP, Exporting to STL, Files in cad/ directory, Print Settings Summary, SpiderPi CAD Package - Ready to Print

### Community 61 - "SpiderPi Wiring Diagram - Desktop 1m Profile"
Cohesion: 0.29
Nodes (6): DRV8825 Board Layout (per driver), Frame Layout (top view, 1m x 1m), GPIO Assignment for Desktop 1m, Power Distribution, Safety Connections, SpiderPi Wiring Diagram - Desktop 1m Profile

### Community 62 - "Hardware Gate Integration Guide"
Cohesion: 0.29
Nodes (6): Gate Sources, Hardware Gate Integration Guide, Hardware Mode, Integration Points in main.py, Overview, Simulator Mode

### Community 63 - "SpiderPi - Cable Robot Simulator and Controller"
Cohesion: 0.29
Nodes (6): Documentation, License, Project Structure, Quick Start (Docker), Quick Start (Mac Simulator), SpiderPi - Cable Robot Simulator and Controller

### Community 64 - "CalibrationStep"
Cohesion: 0.40
Nodes (4): CalibrationState, CalibrationStep, Enum, str

### Community 65 - "SpiderCAM Bill of Materials - Regional Notes"
Cohesion: 0.33
Nodes (5): Europe (EUR), General Sourcing Notes, India (INR), SpiderCAM Bill of Materials - Regional Notes, USA (USD)

### Community 66 - "SpiderCAM Desktop 1m Frame - Wiring Diagram"
Cohesion: 0.33
Nodes (5): Cable Routing, Motor Wiring (NEMA 17 4-wire), RPi 4B Pin Connections, SpiderCAM Desktop 1m Frame - Wiring Diagram, System Overview

### Community 67 - "SpiderCAM Mechanical Drawings and Dimensions"
Cohesion: 0.33
Nodes (5): Anchor Points, Frame Specifications (default 1m x 1m x 1m), SpiderCAM Mechanical Drawings and Dimensions, Spool Dimensions, Workspace Envelope

### Community 68 - "SpiderCAM - Raspberry Pi Cable Robot Camera System"
Cohesion: 0.33
Nodes (5): Key Documentation, Project Structure, Quick Start (Docker), Quick Start (Simulator), SpiderCAM - Raspberry Pi Cable Robot Camera System

### Community 69 - "SpiderCAM Spool Design Specification"
Cohesion: 0.33
Nodes (5): Key Geometry, Load Calculations (1m frame, 0.5 kg payload), Motor Shaft Interface, Print Settings, SpiderCAM Spool Design Specification

### Community 71 - "SpiderPi Wiring Table"
Cohesion: 0.33
Nodes (5): Current Limit Formula, DRV8825 Microstepping Config for 1/16 step, Limit Switch Wiring, Pi GPIO Header Map (BCM numbering), SpiderPi Wiring Table

### Community 72 - "SpiderCAM CAD Drawings Status"
Cohesion: 0.40
Nodes (4): Available OpenSCAD Files, Export STL, Slicer Settings, SpiderCAM CAD Drawings Status

### Community 73 - "SpiderCAM Hardware Gate Integration"
Cohesion: 0.40
Nodes (4): Adding Custom Gates, API Gate Responses, Gate Sequence, SpiderCAM Hardware Gate Integration

### Community 74 - "SpiderCAM GPIO Wiring Table"
Cohesion: 0.40
Nodes (4): IMPORTANT NOTES, Limit Switches, RPi 4B GPIO Pin Assignments, SpiderCAM GPIO Wiring Table

### Community 76 - "SpiderPi Regional Bill of Materials"
Cohesion: 0.40
Nodes (4): India Sources, Notes, SpiderPi Regional Bill of Materials, US Sources

## Knowledge Gaps
- **342 isolated node(s):** `1. Frame Assembly`, `2. Motor Mounting`, `3. Spool Installation`, `4. Cable Rigging`, `5. Electronics Assembly` (+337 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `startup()` connect `spiderpi-sim-starter/backend/main.py` to `from-cowork-original/backend/main.py`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `startup()` connect `from-cowork-original/backend/main.py` to `GPIOMotionBackend`, `motor_metrics`, `load_config`, `HardwareRuntime`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `build_backend()` connect `GPIOMotionBackend` to `SimMotionBackend`, `load_config`, `from-cowork-original/backend/main.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `MotionExecutor` (e.g. with `ControllerManager` and `RuntimeContext`) actually correct?**
  _`MotionExecutor` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `RuntimeContext` (e.g. with `BaseController` and `MotionExecutor`) actually correct?**
  _`RuntimeContext` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `HardwareRuntime` (e.g. with `BoundsCmd` and `ConfigUpdateCmd`) actually correct?**
  _`HardwareRuntime` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `FaultManager` (e.g. with `BoundsCmd` and `ConfigUpdateCmd`) actually correct?**
  _`FaultManager` has 15 INFERRED edges - model-reasoned connections that need verification._