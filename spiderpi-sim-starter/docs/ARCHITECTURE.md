# Architecture

## Overview

The project is a two-process local application:

1. A FastAPI backend simulates Spidercam motion, owns the authoritative machine state, and exposes that state over HTTP and WebSocket.
2. A Vite/React frontend connects to the backend, renders the state in 3D and 2D, and sends control commands back to the backend.

The codebase is intentionally small and monolithic. The backend keeps state in process memory, and the frontend uses a single custom hook for transport and state subscription.

## High-level flow

```text
UI buttons / path actions
        |
        v
frontend/src/hooks/useSpiderSocket.ts
        |
        v
WebSocket messages -> backend/main.py
        |
        v
STATE mutation + simulation loop + path progression
        |
        v
HTTP snapshot (/state) and WebSocket broadcasts (/ws)
        |
        v
React components re-render telemetry, map, and 3D scene
```

## Backend

### Responsibility split

- `backend/main.py`
  Runs the FastAPI app, owns the global simulator state, starts background loops, handles REST and WebSocket commands, and computes cable lengths, spool movement, and motor step deltas.
- `backend/planner.py`
  Generates waypoint lists for predefined paths. Current built-in shapes are `square` and `circle`.
- `backend/persistent_config.py`
  Defines the typed YAML configuration model and persists it to `data/spiderpi.yaml`.

### Core state model

`backend/main.py` stores the entire simulator in a module-level `STATE` dictionary. Important fields:

- `position`: current XYZ carriage position
- `target`: active motion target
- `status`: `idle`, `moving`, or `stopped`
- `estop`: emergency-stop latch
- `anchors`: frame anchor coordinates loaded from config
- `bounds`: XYZ travel limits loaded from config
- `lengths`: computed cable lengths from each anchor to the carriage
- `steps`: accumulated motor step deltas per cable
- `spools`: accumulated spool rotation derived from cable movement
- `trail`: recent position history, capped to 250 points
- `path`: current path name, waypoint index, and remaining point list

This is a simple architecture, but it means there is no persistence for runtime state beyond the YAML config. Restarting the process resets motion state.

### Startup sequence

At import/startup time:

1. `load_config()` reads or creates `data/spiderpi.yaml`.
2. Backend globals are derived from config: anchors, bounds, spool radius, motor step resolution, and microstepping.
3. `STATE` is initialized with a default centered position.
4. On FastAPI startup, two background tasks are scheduled:
   - `sim_loop()`: advances the robot state at roughly 60 Hz
   - `push_loop()`: broadcasts snapshots to WebSocket clients at roughly 20 Hz

### Motion model

The simulator uses a straightforward point-to-point motion model:

- `set_target()` clamps requested XYZ targets to configured bounds.
- `sim_loop()` computes the vector from current position to target.
- Motion advances by `speed * dt` per tick.
- When the target is nearly reached, the loop either advances to the next path waypoint or returns to `idle`.

Cable and motor calculations are derived from geometry:

- `lengths_from_xyz()` computes each cable length with Euclidean distance from carriage to anchor.
- `steps_from_delta_length()` converts cable length delta into motor steps using spool circumference, steps per revolution, and microsteps.
- `spools` tracks accumulated angular displacement as `delta_length / spool_radius`.

This is purely kinematic. There is no acceleration profile, no tension model, no collision checking, and no dynamics beyond constant-speed stepping toward the target.

### Transport layer

The backend exposes both HTTP and WebSocket interfaces:

- HTTP is used once on frontend startup to fetch an initial snapshot from `GET /state`.
- WebSocket is used for:
  - streaming live state to connected clients
  - receiving `jog`, `move`, `path`, `stop`, `estop`, and `reset-estop` commands

The `Manager` class in `main.py` is a minimal connection registry that accepts clients, broadcasts JSON payloads, and drops dead sockets.

## Frontend

### Responsibility split

- `frontend/src/hooks/useSpiderSocket.ts`
  Central transport hook. Fetches the initial HTTP snapshot, opens the WebSocket, reconnects on close, stores the current `SpiderState`, and exposes imperative command helpers.
- `frontend/src/App.tsx`
  Top-level composition. Wires the socket hook to the UI panels.
- `frontend/src/components/Controls.tsx`
  Sends jog, path, stop, and e-stop actions.
- `frontend/src/components/SpiderScene.tsx`
  Renders the robot in 3D using React Three Fiber and Drei.
- `frontend/src/components/TopMap.tsx`
  Renders a simple top-down XY map.
- `frontend/src/components/Telemetry.tsx`
  Displays connection and state values.
- `frontend/src/types.ts`
  Defines the TypeScript shape of the backend state.

### State flow

The frontend does not maintain a separate domain model. It renders the backend state almost directly:

1. `useSpiderSocket()` fetches `GET /state`.
2. The same hook opens `ws://127.0.0.1:8000/ws`.
3. Incoming `type: "state"` messages replace the React state object.
4. Components receive `state` as props and render from it.

This keeps the frontend simple, but it also means the backend contract is effectively the frontend store schema.

### Rendering model

The UI is split into two columns:

- Left: `SpiderScene`
- Right: controls, XY map, and telemetry

The 3D scene converts backend coordinates into a Three.js-friendly arrangement:

- Backend uses `{ x, y, z }`
- Scene maps those to `[x, z, y]`

The scene renders:

- a rectangular frame outline
- four cable lines from anchors to carriage
- a trail polyline
- anchor cubes
- a carriage sphere and body
- an HTML overlay with live XYZ coordinates

### Frontend constraints and caveats

- Backend URLs are hardcoded in `useSpiderSocket.ts`; there is no environment-based configuration.
- `SpiderScene.tsx` uses fixed anchor coordinates instead of `state.anchors`, so custom backend anchor configs will not be reflected visually.
- The reconnect strategy is a simple `setTimeout(connect, 1000)` loop.
- Commands are sent only over WebSocket, even though HTTP endpoints exist for move/path/stop/e-stop actions.

## Configuration model

`persistent_config.py` defines a typed config tree with Pydantic:

- `FrameConfig`
  Frame anchors, travel bounds, spool radius, and motor step resolution
- `RigConfig`
  Physical properties such as carriage mass, payload, speed, and acceleration limits
- `MotorTuning`
  Electrical and stepping parameters
- `gpio_map` and `limit_switches`
  Hardware-oriented placeholders for a future real controller
- `CalibrationState`
  Homing, offsets, measured spool radius, and notes

Although several fields look hardware-specific, the current simulator uses only:

- `frame.anchors`
- `frame.bounds`
- `frame.spool_radius_m`
- `frame.motor_steps_per_rev`
- `motors.microsteps`

The rest of the config is modeled but not consumed by the runtime logic yet.

## Build and run model

### Backend

- Dependency management is file-based through `requirements.txt`
- Runtime server is `uvicorn`
- There is no packaging, migration, or separate worker process

### Frontend

- Toolchain is Vite + TypeScript + React
- `npm run dev` starts the development server
- `npm run build` runs `tsc -b && vite build`
- `npm run preview` serves the production bundle locally

## Operational assumptions

- The backend is expected on `127.0.0.1:8000`.
- The frontend is expected on `127.0.0.1:5173` in development.
- The backend should be launched from the `backend/` directory if you want the config file to resolve to `backend/data/spiderpi.yaml`.

## Missing pieces

The current starter is intentionally narrow. Things not present in the source:

- automated tests
- environment-variable based configuration
- authentication or authorization
- production deployment manifests
- real hardware motor/GPIO drivers
- richer path planning or physics
