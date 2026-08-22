# SpiderPi - Cable Robot Simulator and Controller

A four-cable parallel robot (cable-driven parallel robot) inspired by
stadium Spidercam systems, implemented as a Raspberry Pi home build
with a React + Three.js simulator dashboard.

## Quick Start (Mac Simulator)

    cd backend
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    SPIDERPI_SIM_GPIO=1 uvicorn main:app --reload --port 8000

    # In a new terminal
    cd frontend
    npm install && npm run dev

    # Open http://localhost:5173

## Quick Start (Docker)

    docker compose up --build
    # Open http://localhost:5173

## Project Structure

    backend/     FastAPI Python backend (motion, physics, config, WebSocket)
    frontend/    React + Three.js dashboard (3D view, controls, telemetry)
    data/        Runtime YAML (config, paths, calibration state)
    profiles/    Machine profiles (desktop_1m, room_1p5m, room_2m)
    cad/         OpenSCAD spool and mount designs
    bom/         Bill of materials (India and US)
    docs/        Hardware build, wiring, troubleshooting guides

## Documentation

BUILD_GUIDE.md              - Hardware assembly guide
WIRING_TABLE.md             - GPIO pin mapping and wiring
REAL_HARDWARE_BRINGUP.md    - Pi deployment guide
CALIBRATION_CHECKLIST.md    - Step-by-step calibration
MECHANICAL_DRAWINGS.md      - Dimensions and geometry
SPOOL_DESIGN_SPEC.md        - Spool fabrication spec
RUNBOOK.md                  - Complete operational runbook

## License

MIT License - see LICENSE file
