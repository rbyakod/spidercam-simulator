# SpiderPi System Runbook

## System Overview

SpiderPi is a four-cable parallel robot simulator and control system.
It consists of:
- FastAPI Python backend (runs on Mac for simulation, Pi for hardware)
- React + Three.js frontend (runs in browser on any machine)
- Optional Raspberry Pi GPIO layer (real hardware mode)
- WebSocket real-time communication

## Directory Structure

    spiderpi-sim/ (or SpiderCAM Design - perplexity-files/)
    |-- backend/          Python FastAPI backend
    |-- frontend/         React + Vite frontend
    |-- data/             Runtime YAML data files
    |-- profiles/         Machine configuration profiles
    |-- cad/              OpenSCAD design files
    |-- bom/              Bills of materials
    |-- docs/hardware/    Hardware documentation

## Prerequisites

### macOS (simulation mode)
    python3 --version     # Need 3.11+
    node --version        # Need 18+
    npm --version         # Need 9+

### Raspberry Pi (hardware mode)
    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod
    systemctl status pigpiod   # Must show active

## Running the Backend

### Step 1: Create virtual environment (first time only)
    cd backend
    python3 -m venv .venv

### Step 2: Activate virtual environment
    source .venv/bin/activate       # macOS/Linux
    .venv\Scripts\activate         # Windows

### Step 3: Install dependencies (first time only)
    pip install -r requirements.txt

### Step 4: Start the backend
    # Simulation mode (macOS or Pi without GPIO)
    SPIDERPI_SIM_GPIO=1 uvicorn main:app --reload --host 0.0.0.0 --port 8000

    # Hardware mode (Raspberry Pi only)
    SPIDERPI_SIM_GPIO=0 uvicorn main:app --host 0.0.0.0 --port 8000

### Verify backend is running
    curl http://localhost:8000/state
    curl http://localhost:8000/docs    # Swagger UI

## Running the Frontend

### Step 1: Install dependencies (first time only)
    cd frontend
    npm install

### Step 2: Start development server
    npm run dev

### Step 3: Open browser
    Open http://localhost:5173

### Environment variables (optional)
    VITE_API_URL=http://raspberrypi.local:8000
    VITE_WS_URL=ws://raspberrypi.local:8000/ws

## Running with Docker Compose

### Start all services
    docker compose up --build

### Stop all services
    docker compose down

### View logs
    docker compose logs -f backend
    docker compose logs -f frontend

### Rebuild after code changes
    docker compose up --build

## API Reference

### REST Endpoints

GET /state              - Full system state JSON
GET /config             - Current system configuration
POST /config            - Update system configuration
POST /move              - Move to absolute position {x, y, z, speed}
POST /path              - Run named path {name, speed, size, radius, z}
POST /stop              - Stop current motion
POST /estop             - Emergency stop
POST /reset-estop       - Reset emergency stop
GET /switches           - Read limit switch states
GET /faults             - Current and historical faults
POST /faults/reset      - Clear current fault
POST /home/run          - Run homing sequence
GET /profiles           - List machine profiles
POST /profiles/{name}/apply - Apply named profile
POST /profiles/save-current - Save current config as profile
GET /paths              - List saved paths and poses
POST /paths/replay/{name}   - Replay saved path
POST /record/start      - Start recording movement
POST /record/stop       - Stop recording
POST /record/save       - Save recorded path {name, points, speed}
GET /wizard             - Calibration wizard state
GET /wizard/checklist   - Full checklist with tasks
POST /wizard/step       - Mark step done/undone
POST /wizard/reset      - Reset all wizard progress

### WebSocket /ws

Client sends JSON messages:
    {type: "ping"}                          - Heartbeat
    {type: "jog", dx, dy, dz, speed}       - Relative move
    {type: "move", x, y, z, speed}         - Absolute move
    {type: "preset", name, speed}          - Move to preset
    {type: "path", name, speed, z, ...}    - Run path
    {type: "home"}                          - Home to center
    {type: "stop"}                          - Stop motion
    {type: "estop"}                         - Emergency stop
    {type: "reset-estop"}                  - Reset e-stop

Server sends:
    {type: "state", ...full state...}      - State update at 20 Hz
    {type: "pong"}                          - Ping response

## Common Workflows

### Workflow 1: Start simulator on macOS

    cd backend
    source .venv/bin/activate
    SPIDERPI_SIM_GPIO=1 uvicorn main:app --reload --port 8000 &

    cd ../frontend
    npm run dev

    # Open http://localhost:5173

### Workflow 2: Change machine profile

    1. Open dashboard in browser
    2. Scroll to Profile Selector panel
    3. Select desired profile (desktop_1m, room_1p5m, room_2m)
    4. Click Apply Profile
    5. Frame Sizing panel updates automatically
    6. 3D scene reflects new geometry

### Workflow 3: Run a preset path

    Option A - Dashboard:
    1. Click Controls panel
    2. Click Square path, Circle path, or Diagonal

    Option B - API:
    curl -X POST http://localhost:8000/path             -H Content-Type: application/json             -d {"name":"square","speed":0.3,"size":0.8,"z":0.9}

### Workflow 4: Save a custom path

    1. Click Start record in HomingPanel
    2. Use joystick or click map to move carriage
    3. Click Stop record
    4. Enter path name and click Save
    5. Path appears in replay list

### Workflow 5: Calibration wizard

    1. Open Calibration Wizard panel in dashboard
    2. Select machine profile and apply
    3. Work through each step in order
    4. Mark each step done when complete
    5. Final step saves verified configuration

### Workflow 6: Deploy to Raspberry Pi

    1. SSH to Pi: ssh pi@raspberrypi.local
    2. Clone project: git clone <your-repo>
    3. cd spiderpi-sim/backend
    4. python3 -m venv .venv && source .venv/bin/activate
    5. pip install -r requirements.txt
    6. sudo systemctl start pigpiod
    7. SPIDERPI_SIM_GPIO=0 uvicorn main:app --host 0.0.0.0 --port 8000

    From MacBook frontend:
    VITE_API_URL=http://raspberrypi.local:8000         VITE_WS_URL=ws://raspberrypi.local:8000/ws         npm run dev

## Troubleshooting

Backend won't start:
    Verify Python 3.11+: python3 --version
    Activate venv: source .venv/bin/activate
    Check requirements: pip install -r requirements.txt
    Check port: lsof -i :8000

Frontend won't connect:
    Verify backend running: curl http://localhost:8000/state
    Check browser console for WebSocket errors
    Verify VITE_WS_URL matches backend address

pigpiod not found (Pi):
    sudo apt install pigpio
    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod

Motors not moving (Pi hardware mode):
    Check pigpiod running
    Verify GPIO wiring with multimeter
    Check SPIDERPI_SIM_GPIO=0 is set
    Verify DRV8825 VMOT has 12V
    Check shared ground connection

3D scene blank:
    Check browser supports WebGL (Chrome/Firefox recommended)
    Refresh page after backend starts
    Check console for Three.js errors

## Production Checklist (before any hardware run)

- [ ] pigpiod service running on Pi
- [ ] All limit switches reading idle in /switches
- [ ] E-stop circuit verified working
- [ ] Machine profile matches physical geometry
- [ ] Max speed set conservatively (0.2-0.3 m/s for first runs)
- [ ] Carriage mass within limits (< 500g)
- [ ] All cables pre-tensioned, none slack
- [ ] Working area clear of people and obstacles
- [ ] Emergency stop reachable from operator position

## Monitoring

Backend health: GET http://localhost:8000/state
Physics overload: check state.physics.overload
Temperature: check state.physics.hottest_temp_c (warn > 70C)
Fault state: check state.fault_info.active
Limit switches: check state.limit_switches

## File Locations

Config: data/spiderpi.yaml (auto-created on first run)
Path presets: data/path_presets.yaml
Calibration state: data/calibration_wizard.yaml
Machine profiles: profiles/machine_profiles.yaml

All YAML files are human-readable and can be edited directly.
Restart backend after manual YAML edits.

## Version History

v0.1-sim: Mac simulator, no GPIO, full dashboard
v0.2-physics: Motor physics simulation added
v0.3-paths: Path planner (square, circle, diagonal) added
v0.4-calibration: Calibration wizard and persistent config added
v0.5-hardware: GPIO backend, limit monitor, homing controller
v0.6-profiles: Machine profiles and frame sizing panel
v0.7-recording: Path recording and replay
v0.8-gates: Hardware-gated calibration wizard
