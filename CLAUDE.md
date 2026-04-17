# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Spidercam-style cable robot simulator. FastAPI backend owns authoritative state, streams it over WebSocket. React + Three.js frontend renders 3D scene, XY map, telemetry, and sends control commands back. All local, no persistence beyond a YAML config file.

The actual codebase lives in `spiderpi-sim-starter/`. The root also contains a scaffold script (`create_spiderpi_sim.sh`) and an `index.html` stub.

## Commands

### Backend (from `spiderpi-sim-starter/backend/`)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Syntax check (no venv needed):
```bash
python3 -m py_compile backend/main.py backend/planner.py backend/persistent_config.py
```

### Frontend (from `spiderpi-sim-starter/frontend/`)

```bash
npm install
npm run dev -- --host 127.0.0.1 --port 5173
npm run build          # tsc -b && vite build
npm run preview        # serve production bundle
```

No test suite exists yet.

## Architecture

Two-process local app. Backend on `127.0.0.1:8000`, frontend on `127.0.0.1:5173`.

### Backend (`spiderpi-sim-starter/backend/`)

- **`main.py`** — FastAPI app, global `STATE` dict (module-level), sim loop at ~60 Hz, WebSocket broadcast at ~20 Hz. Computes cable lengths (Euclidean), motor step deltas, and spool rotation from carriage position. No database, no acceleration profiles, no tension model.
- **`planner.py`** — Generates waypoint lists for `square` and `circle` paths. Pure functions, no state.
- **`persistent_config.py`** — Pydantic config model persisted to `data/spiderpi.yaml`. Runtime only uses `frame.anchors`, `frame.bounds`, `frame.spool_radius_m`, `frame.motor_steps_per_rev`, `motors.microsteps`. Hardware-oriented fields (GPIO, limit switches, calibration) are modeled but unused.

State model: `position`, `target`, `status` (idle/moving/stopped), `estop` latch, `lengths`, `steps`, `spools`, `trail` (capped 250 points), `path` (name + waypoint index + point list).

Transport: `GET /state` for initial snapshot. `WS /ws` for live state streaming and command input (`jog`, `move`, `path`, `stop`, `estop`, `reset-estop`). HTTP POST endpoints mirror the WS commands.

### Frontend (`spiderpi-sim-starter/frontend/`)

- **`src/hooks/useSpiderSocket.ts`** — Single custom hook. Fetches HTTP snapshot, opens WebSocket, reconnects on close (1s retry), exposes imperative command helpers. URLs hardcoded to `127.0.0.1:8000`.
- **`src/types.ts`** — `SpiderState` type mirrors the backend STATE shape exactly.
- **`src/App.tsx`** — Two-column layout: left = 3D scene, right = controls + map + telemetry.
- **`src/components/SpiderScene.tsx`** — React Three Fiber. Coordinate mapping: backend `{x,y,z}` → Three.js `[x, z, y]`. Anchor positions are hardcoded, not read from `state.anchors`.
- **`src/components/TopMap.tsx`** — SVG XY top-down map (position dot only).
- **`src/components/Controls.tsx`** — Jog buttons, path buttons, stop/e-stop.
- **`src/components/Telemetry.tsx`** — Connection status and state values.

### Key constraints

- Runtime state is in-memory only. Process restart resets all motion state.
- Backend must be launched from `backend/` directory for config path to resolve correctly.
- 3D scene anchors are hardcoded in `SpiderScene.tsx` — changing backend anchor config won't update the visual.
- No environment-based configuration — URLs are hardcoded in the frontend hook.
- CORS is open to all origins.
- No automated tests, no authentication, no production deployment setup.
