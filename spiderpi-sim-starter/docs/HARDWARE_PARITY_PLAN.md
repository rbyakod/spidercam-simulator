# Hardware Parity Plan

## Purpose

This document defines how to evolve the current SpiderPi simulator into a system that is suitable for future hardware parity.

The core objective is:

- the same command model, geometry, safety rules, and telemetry should apply in both simulator and hardware modes
- only the execution backend should differ: simulated winches vs real motor and GPIO control

This is a design and sequencing document. It does not propose immediate runtime changes.

## Current Gap

The current project is useful as a visual simulator, but it is not yet a hardware-faithful machine model.

### What is already usable

- frame anchors are configurable
- cable lengths are computed from geometry
- motor step deltas are derived from cable length deltas
- the frontend and backend already share a simple state contract
- the config model already has placeholders for calibration, GPIO, and motion tuning

### What is not hardware-parity ready

- motion is currently driven by direct Cartesian interpolation, then cable lengths are derived afterward
- workspace safety is a fixed XYZ clamp instead of a geometry-aware reachable workspace
- there is no explicit machine state model for arming, homing, calibration, fault, or hardware readiness
- simulator and hardware execution are not separated behind a common interface
- the frontend can currently display geometry that does not match the backend anchors
- there is no deterministic motion execution layer for real motors
- there are no validation tests for kinematics, calibration, or safety rules

## Design Goals

1. The simulator and hardware controller must accept the same commands.
2. The simulator and hardware controller must emit the same state schema.
3. Real anchor geometry must be authoritative everywhere.
4. Calibration and homing must be first-class workflows, not comments in config.
5. Safety checks must be based on machine geometry and configuration, not only on XYZ bounds.
6. The simulator must model the machine through cable-space execution, not shortcut around it.
7. The frontend must become an engineering view first and a stylized view second.

## Non-Goals

- full high-fidelity physics in the first refactor
- advanced cable sag simulation in the first refactor
- autonomous camera path optimization
- production deployment hardening

## Target Architecture

The recommended backend shape is:

```text
API layer
  -> command validation
  -> machine state manager
  -> planner
  -> kinematics/workspace validator
  -> motion executor
      -> simulator controller
      -> hardware controller
  -> telemetry/state publisher
```

### Module boundaries

#### `machine_state`

Owns the authoritative machine state and transition rules.

Responsibilities:

- machine mode and status transitions
- estop and fault latching
- active target and active path bookkeeping
- homing and calibration progress
- controller health and readiness

#### `planner`

Produces waypoint or trajectory targets in Cartesian space.

Responsibilities:

- square, circle, and future path generators
- optional feedrate, dwell, and trajectory metadata
- path pre-validation before execution

#### `kinematics`

Converts between carriage pose and cable lengths.

Responsibilities:

- forward state representation in cable space
- inverse mapping from XYZ target to per-cable target lengths
- per-anchor geometry checks
- consistency checks against calibration offsets

For the current scope, inverse kinematics is simple because the command origin is still XYZ and the output is cable length targets.

#### `workspace`

Determines whether a requested position is valid for the configured machine.

Responsibilities:

- reachable workspace checks from anchor geometry
- minimum and maximum cable length checks
- minimum height and frame clearance checks
- cable angle and geometry guardrails
- tension-feasibility placeholders for future expansion

This replaces the current fixed-bounds-only model as the real safety gate.

#### `executor`

Turns validated targets into time-based cable movement commands.

Responsibilities:

- synchronize cable target updates
- velocity and acceleration limiting
- stop, estop, and resume behavior
- deterministic tick/update model

This layer must be shared by both simulator and hardware controllers.

#### `controllers/sim_controller`

Consumes cable targets and updates simulated actuator state.

Responsibilities:

- simulate step execution or cable-length execution
- publish resulting cable lengths, step counters, and derived carriage pose
- expose the same readiness and fault fields as hardware mode

The simulator should no longer move the carriage directly in XYZ and back-compute cable lengths after the fact.

#### `controllers/hardware_controller`

Consumes the same cable targets but drives real motors and reads real IO.

Responsibilities:

- motor enable/disable
- synchronized step output
- direction pin control
- limit switch reads
- homing and zeroing routines
- fault and estop propagation

## Required Machine State Model

The current `idle/moving/stopped` status model is too small for hardware parity.

Recommended top-level fields:

- `mode`: `sim`, `hardware`, `dry_run`
- `status`: `booting`, `idle`, `moving`, `homing`, `calibrating`, `estopped`, `fault`
- `armed`: boolean
- `homed`: per-axis or per-corner status
- `faults`: active fault list
- `warnings`: active warning list
- `controller_ready`: boolean
- `geometry_valid`: boolean
- `calibration_valid`: boolean

Recommended command preconditions:

- no motion allowed while `estopped`
- no hardware motion allowed while `controller_ready` is false
- no normal move/path allowed until homing/calibration requirements are satisfied
- only explicit override flows may bypass those checks

## Geometry and Configuration Requirements

The current config model is a good start but needs clearer separation between machine geometry and runtime state.

### Keep in config

- anchor coordinates
- spool geometry
- steps per revolution
- microsteps
- motor direction inversion
- limit switch wiring
- travel policy
- max speed and acceleration
- payload and carriage mass

### Add to config

- per-corner spool radius, not only a single frame radius
- per-corner cable minimum and maximum safe lengths
- per-corner calibration zero offsets
- frame safety margins
- minimum safe cable angle
- machine identifier and controller mode defaults

### Remove from visual-only interpretation

- no display-only anchor scaling in engineering mode
- no alternate rendered tower positions unless explicitly labeled as stylized

## Motion Model Changes Needed

The most important architectural change is this:

### Current model

1. Accept XYZ target
2. Move the carriage directly toward target
3. Derive cable lengths from the new XYZ
4. Derive motor steps from cable length deltas

### Hardware-parity model

1. Accept XYZ target
2. Validate target against machine workspace
3. Convert target to per-cable target lengths
4. Execute synchronized cable motion with speed and acceleration rules
5. Derive carriage pose and telemetry from resulting cable state

The second model is what allows simulator and hardware to share the same execution logic.

## Safety Model Changes Needed

The current bounds clamp is not enough.

The future safety pipeline should be:

1. command validation
2. state precondition validation
3. geometry/workspace validation
4. controller readiness validation
5. execution-time monitoring

Initial safety checks to implement:

- target must be inside configured geometric workspace
- no cable length may exceed configured safe bounds
- minimum carriage height must be maintained
- target may not be accepted when calibration is invalid
- estop must halt execution immediately and latch until reset

Future safety checks:

- cable angle floor
- estimated tension floor
- acceleration-limited motion feasibility
- collision regions for pitch, towers, or stadium structures if needed

## Frontend Requirements For Parity

The frontend should become an observer and command client for the real machine model.

Requirements:

- render anchors from backend geometry only
- label simulator vs hardware mode clearly
- show homing, calibration, estop, and fault status
- show both Cartesian pose and per-cable telemetry
- expose dry-run mode separately from live hardware mode
- keep stylized visuals optional, not the default engineering source of truth

Recommended extra telemetry:

- cable lengths per corner
- target cable lengths
- step rates
- controller readiness
- calibration validity
- workspace-valid or out-of-workspace indicator

## Testing and Verification Plan

Hardware parity will fail without tests.

### Unit tests

- cable length calculations from anchor geometry
- step conversion math
- workspace validation on known good and bad positions
- calibration offset application
- state machine transitions

### Golden geometry tests

Use a fixed anchor layout and verify:

- center point lengths
- near-corner point lengths
- low-height point validity
- symmetric moves produce symmetric cable deltas

### Simulation contract tests

- same command accepted in sim and dry-run modes
- both modes emit the same state schema
- estop behavior is identical across modes

### Hardware dry-run tests

- log generated step commands without energizing motors
- verify homing sequences against expected switch events
- replay dry-run traces in simulator

### Hardware-in-the-loop tests

- one motor at a time
- then paired corners
- then full frame synchronized motion

## Recommended Phased Implementation

### Phase 0: Freeze current behavior and write spec

- document current limits
- stop adding visual-only geometry hacks to the engineering path
- decide the canonical state contract

Exit criteria:

- design approved
- state fields and command semantics agreed

### Phase 1: Extract machine core

- split `main.py` into machine state, planner, kinematics, workspace, executor
- keep current simulator behavior initially, but move it behind explicit modules

Exit criteria:

- backend behavior preserved
- architecture no longer monolithic

### Phase 2: Add explicit state machine and controller abstraction

- add controller interface
- add `sim`, `hardware`, and `dry_run` modes
- add status and fault fields

Exit criteria:

- same API works across controller modes
- frontend can display mode and readiness

### Phase 3: Replace fixed-bounds-only logic with workspace validation

- keep old bounds as a secondary clamp if useful
- introduce geometry-derived validity checks

Exit criteria:

- invalid geometric targets are rejected before execution
- tests cover known edge positions

### Phase 4: Move simulator to cable-space execution

- simulator consumes cable targets
- simulator emits cable state and derived pose
- direct Cartesian stepping is removed from the core path

Exit criteria:

- simulator path matches the future hardware command path

### Phase 5: Implement calibration and homing

- zero offsets
- homing routines
- readiness gates

Exit criteria:

- machine cannot enter normal motion before valid setup

### Phase 6: Add hardware controller and dry-run mode

- GPIO and motor driver integration
- limit switch handling
- motor synchronization

Exit criteria:

- dry-run and live hardware share the same executor contract

### Phase 7: Upgrade frontend for engineering fidelity

- render exact anchor geometry
- add machine status and calibration views
- make stylized stadium view optional

Exit criteria:

- frontend can be trusted for machine state interpretation

## Acceptance Criteria For Hardware-Parity Readiness

The system is ready for early hardware hookup when all of the following are true:

- simulator and hardware expose the same API and state schema
- real anchor geometry is used everywhere by default
- geometric workspace validation is active
- calibration and homing flows exist and gate motion
- estop semantics are identical in sim and hardware modes
- dry-run mode can generate and log motor commands without motion
- unit and contract tests cover kinematics, safety, and state transitions

## Immediate Recommendation

Before any hardware-related code changes:

1. approve the target state schema
2. approve the controller abstraction
3. decide whether engineering view and stadium view should be separate frontend modes
4. decide whether spool radius is modeled globally or per corner

Those decisions will shape the first refactor and avoid rework.
