# SpiderPi Simulator Starter

Local simulator for a Spidercam-style cable robot using FastAPI on the backend and React + Three.js on the frontend.

Detailed architecture notes live in [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## v14

Before making this simulator real world true engineering simulator with GPIO, physics and math compatibility with real world coordinates - after this all tags indicate changes to the simulator to follow resl world physics/math.

## Repository layout

```text
spiderpi-sim-starter/
├── backend/
│   ├── main.py
│   ├── persistent_config.py
│   ├── planner.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── docs/
    └── ARCHITECTURE.md
```

## What the app does

The backend simulates a four-cable Spidercam carriage inside configured XYZ bounds. It exposes the current state over both HTTP and WebSocket. The frontend subscribes to that state, renders the robot in 3D, shows a top-down map and telemetry, and sends jog/path control commands back over the WebSocket connection.

## Prerequisites

- Python 3.12 or newer is recommended
- Node.js 22 and npm 11 were available in the inspection environment

## Install dependencies

### Backend

Run these commands from `spiderpi-sim-starter/backend`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend

Run these commands from `spiderpi-sim-starter/frontend`:

```bash
npm install
```

## Run in development

Start the backend first:

```bash
cd spiderpi-sim-starter/backend
source .venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Then start the frontend in a second terminal:

```bash
cd spiderpi-sim-starter/frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173`.

### macOS one-shot launcher

Run this from the repository root to open both processes in Terminal:

```bash
ROOT="/Users/ravibyakod/WORK/SpiderCam/spiderpi-sim-starter"
osascript \
  -e 'tell application "Terminal"' \
  -e "do script \"cd $ROOT/backend && source .venv/bin/activate && uvicorn main:app --reload --host 127.0.0.1 --port 8000\"" \
  -e "do script \"cd $ROOT/frontend && npm run dev -- --host 127.0.0.1 --port 5173\"" \
  -e 'activate' \
  -e 'end tell'
```

## Compile / build

### Backend

There is no packaging step for the backend. For a lightweight syntax check, run:

```bash
cd spiderpi-sim-starter
python3 -m py_compile backend/main.py backend/planner.py backend/persistent_config.py
```

To run the backend without auto-reload:

```bash
cd spiderpi-sim-starter/backend
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000
```

### Frontend

Build the production assets with Vite:

```bash
cd spiderpi-sim-starter/frontend
npm run build
```

Preview the production build locally:

```bash
npm run preview -- --host 127.0.0.1 --port 4173
```

## Runtime details

- The frontend is hard-wired to `http://127.0.0.1:8000` and `ws://127.0.0.1:8000/ws` in `src/hooks/useSpiderSocket.ts`.
- The backend creates and reads its YAML config from `data/spiderpi.yaml` relative to the backend working directory.
- CORS is open to all origins in the current starter implementation.

## Main endpoints

- `GET /state`: returns the current simulator state snapshot
- `POST /move`: moves toward a target `{ x, y, z, speed }`
- `POST /path`: runs a named path such as `square` or `circle`
- `POST /stop`: cancels path motion and holds current position
- `POST /estop`: latches emergency stop
- `POST /reset-estop`: clears emergency stop
- `WS /ws`: streams state updates and accepts control messages

## Notes and limitations

- The 3D scene currently hardcodes anchor coordinates in `frontend/src/components/SpiderScene.tsx` instead of rendering `state.anchors`.
- The top-down map renders only the current position, not the configured bounds, anchors, or trail history.
- This starter is a simulator only; GPIO, motor drivers, and real hardware control are represented in config but not implemented.
