# SpiderCAM Runbook - How to Compile and Run All Services

## Prerequisites
- Python 3.10+, Node.js 20+, npm 10+, Docker + docker-compose (optional)

## Option A: Development Mode (Simulator)

### 1. Start Backend
    cd ~/WORK/SpiderCAM\ Design\ -\ perplexity-files/backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    SPIDERPI_SIM_GPIO=1 uvicorn main:app --reload --port 8000

    API:    http://localhost:8000
    Docs:   http://localhost:8000/docs
    Health: http://localhost:8000/health

### 2. Start Frontend (new terminal)
    cd ~/WORK/SpiderCAM\ Design\ -\ perplexity-files/frontend
    npm install
    npm run dev
    # Open http://localhost:5173

### 3. Verify
    curl http://localhost:8000/health
    # Returns: {"status": "ok", "sim": true}

## Option B: Docker Compose

    cd ~/WORK/SpiderCAM\ Design\ -\ perplexity-files/
    docker-compose up --build
    # Backend: http://localhost:8000
    # Frontend: http://localhost:80

    docker-compose up -d --build    # background
    docker-compose logs -f backend  # view logs
    docker-compose down             # stop

## Option C: Real Hardware (Raspberry Pi)

    cd backend && source .venv/bin/activate
    # Remove SPIDERPI_SIM_GPIO or set to 0
    uvicorn main:app --host 0.0.0.0 --port 8000

## Systemd Service (Auto-start on Boot)

Create /etc/systemd/system/spidercam-backend.service:

    [Unit]
    Description=SpiderCAM Backend
    After=network.target

    [Service]
    Type=simple
    User=pi
    WorkingDirectory=/home/pi/WORK/SpiderCAM Design - perplexity-files/backend
    Environment=SPIDERPI_SIM_GPIO=1
    ExecStart=/home/pi/WORK/SpiderCAM Design - perplexity-files/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
    Restart=always

    [Install]
    WantedBy=multi-user.target

    sudo systemctl daemon-reload
    sudo systemctl enable spidercam-backend
    sudo systemctl start spidercam-backend

## API Endpoints Reference

| Method | Endpoint              | Description                  |
|--------|-----------------------|------------------------------|
| GET    | /health               | Health check                 |
| GET    | /api/status           | Current position and state   |
| POST   | /api/move             | Move to XYZ position         |
| POST   | /api/jog              | Jog single axis              |
| POST   | /api/estop            | Emergency stop               |
| POST   | /api/fault/clear      | Clear active faults          |
| POST   | /api/home             | Run homing sequence          |
| GET    | /api/home/status      | Homing state                 |
| POST   | /api/calibrate        | Compute calibration offsets  |
| GET    | /api/calibrate/status | Calibration state            |
| GET    | /api/paths            | List saved paths             |
| POST   | /api/paths            | Save a path                  |
| POST   | /api/paths/{name}/run | Execute a saved path         |
| DELETE | /api/paths/{name}     | Delete a path                |
| GET    | /api/profiles         | List motion profiles         |
| POST   | /api/profiles         | Save a profile               |
| DELETE | /api/profiles/{name}  | Delete a profile             |
| GET    | /api/gpio             | Get GPIO map                 |
| POST   | /api/gpio             | Update GPIO map              |
| WS     | /ws/telemetry         | Real-time telemetry stream   |

## Environment Variables

| Variable           | Default            | Description               |
|--------------------|--------------------|---------------------------|
| SPIDERPI_SIM_GPIO  | True               | Use simulator (no GPIO)   |
| FRAME_WIDTH        | 1.0                | Frame width in metres     |
| FRAME_HEIGHT       | 1.0                | Frame height in metres    |
| FRAME_DEPTH        | 1.0                | Frame depth in metres     |
| MAX_SPEED          | 0.5                | Max cable speed m/s       |
| MAX_ACCEL          | 1.0                | Max acceleration m/s2     |
| STEPS_PER_REV      | 200                | Motor steps per rev       |
| MICROSTEPS         | 16                 | Microstepping divisor     |
| SPOOL_DIAMETER_MM  | 40.0               | Spool winding diameter mm |
| WS_TICK_HZ         | 50.0               | WebSocket telemetry Hz    |
| GPIO_CONFIG_PATH   | data/spiderpi.yaml | GPIO map file path        |

## Running Tests
    cd backend && source .venv/bin/activate
    pytest -v

## Generate GPIO Map
    cd backend && source .venv/bin/activate
    python gpio_map_example.py

## Export STL from CAD
    openscad -o cad/spool_direct.stl cad/spool_v1_direct_5mm.scad
    openscad -o cad/spool_coupler.stl cad/spool_v1_coupler.scad
    openscad -o cad/corner_mount.stl cad/corner_motor_mount_v1.scad

## Troubleshooting

| Problem                    | Solution                                        |
|----------------------------|-------------------------------------------------|
| Port 8000 in use           | lsof -i :8000, kill the PID                     |
| npm install fails          | Delete node_modules and package-lock.json       |
| WebSocket not connecting   | Verify backend running, check vite.config.ts    |
| Motor not moving           | Check SPIDERPI_SIM_GPIO=0, verify GPIO wiring   |
| Homing fails               | Check limit switch GPIO pins in spiderpi.yaml   |
| Large calibration error    | Re-measure frame dimensions, restart backend    |
| React build fails          | npx tsc --noEmit to see TypeScript errors       |
