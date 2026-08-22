# Graph Report - /Users/ravibyakod/WORK/SpiderCam  (2026-08-22)

## Corpus Check
- 42 files · ~69,032 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 248 nodes · 536 edges · 11 communities (8 shown, 3 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9

## God Nodes (most connected - your core abstractions)
1. `MotionExecutor` - 29 edges
2. `RuntimeContext` - 27 edges
3. `refresh_state()` - 21 edges
4. `BaseController` - 18 edges
5. `with_state_lock()` - 17 edges
6. `compilerOptions` - 15 edges
7. `Manager` - 14 edges
8. `ControllerManager` - 13 edges
9. `HardwareController` - 13 edges
10. `default_state()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `BaseController` --uses--> `RuntimeContext`  [INFERRED]
  spiderpi-sim-starter/backend/controllers/base_controller.py → spiderpi-sim-starter/backend/models.py
- `MotionExecutor` --uses--> `ControllerManager`  [INFERRED]
  spiderpi-sim-starter/backend/executor.py → spiderpi-sim-starter/backend/controllers/controller_manager.py
- `MotionExecutor` --uses--> `RuntimeContext`  [INFERRED]
  spiderpi-sim-starter/backend/executor.py → spiderpi-sim-starter/backend/models.py
- `Manager` --uses--> `MotionExecutor`  [INFERRED]
  spiderpi-sim-starter/backend/main.py → spiderpi-sim-starter/backend/executor.py
- `MotionExecutorTests` --uses--> `MotionExecutor`  [INFERRED]
  spiderpi-sim-starter/backend/tests/test_executor.py → spiderpi-sim-starter/backend/executor.py

## Import Cycles
- None detected.

## Communities (11 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (8): BaseController, ControllerManager, DryRunController, HardwareController, SimController, Manager, MotionExecutorTests, WebSocket

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (40): get, on_event, post, arm(), calibrate(), current_state(), disarm(), estop() (+32 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (23): App(), Controls(), clamp(), DEFAULTS, FramePlanner(), num(), plannerFromState(), PlannerInputs (+15 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (32): react, react-dom, @react-three/drei, @react-three/fiber, dependencies, react, react-dom, @react-three/drei (+24 more)

### Community 4 - "Community 4"
Cohesion: 0.24
Nodes (19): Path, _calibration_defaults(), _calibration_valid(), _calibration_warnings(), _default_mode(), _default_position(), default_state(), _normalize_lengths() (+11 more)

### Community 5 - "Community 5"
Cohesion: 0.10
Nodes (20): DOM, DOM.Iterable, ES2020, src, compilerOptions, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames (+12 more)

### Community 7 - "Community 7"
Cohesion: 0.26
Nodes (7): lengths_from_position(), lengths_from_xyz(), _solve_linear_3x3(), solve_position_from_lengths(), steps_from_delta_length(), build_runtime_context(), KinematicsTests

## Knowledge Gaps
- **46 isolated node(s):** `create_spiderpi_sim.sh script`, `name`, `private`, `version`, `type` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MotionExecutor` connect `Community 6` to `Community 0`, `Community 1`, `Community 4`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `RuntimeContext` connect `Community 4` to `Community 0`, `Community 1`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `BaseController` connect `Community 0` to `Community 4`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `MotionExecutor` (e.g. with `ControllerManager` and `RuntimeContext`) actually correct?**
  _`MotionExecutor` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `RuntimeContext` (e.g. with `BaseController` and `MotionExecutor`) actually correct?**
  _`RuntimeContext` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `BaseController` (e.g. with `RuntimeContext` and `ControllerManager`) actually correct?**
  _`BaseController` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `create_spiderpi_sim.sh script`, `name`, `private` to the rest of the system?**
  _46 weakly-connected nodes found - possible documentation gaps or missing edges._