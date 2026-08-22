# SpiderCAM - Raspberry Pi Cable Robot Camera System

A 4-cable parallel robot camera system built around a Raspberry Pi 4B,
NEMA 17 stepper motors, DRV8825 drivers, and a Python/FastAPI backend
with a React + Three.js frontend.

## Quick Start (Simulator)

    cd backend
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    SPIDERPI_SIM_GPIO=1 uvicorn main:app --reload --port 8000

    # New terminal:
    cd frontend
    npm install && npm run dev
    # Open http://localhost:5173

## Quick Start (Docker)

    docker-compose up --build

## Project Structure

    backend/    FastAPI + WebSocket backend (Python)
    frontend/   React + Three.js UI (TypeScript)
    data/       YAML config and path presets
    profiles/   Motion profiles
    cad/        OpenSCAD mechanical designs
    bom/        Bill of Materials (India, US, regional)
    docs/       Hardware guides, wiring, troubleshooting

## Key Documentation

- BUILD_GUIDE.md          Step-by-step physical build
- WIRING_TABLE.md         GPIO pin assignments
- RUNBOOK.md              How to compile and run all services
- CALIBRATION_CHECKLIST.md  Pre-flight calibration steps
- MECHANICAL_DRAWINGS.md  Frame dimensions and tolerances
