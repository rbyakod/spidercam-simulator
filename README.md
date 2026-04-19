# SpiderCam

This repository currently runs from `spiderpi-sim-starter/`, which contains the simulator backend and frontend.

## Prerequisites

- Python 3.12 or newer
- Node.js 22
- npm 11

## First-Time Setup

```bash
cd spiderpi-sim-starter/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm install
```

## Run The System

Start the backend in one terminal:

```bash
cd /Users/ravibyakod/WORK/SpiderCam/spiderpi-sim-starter/backend
source .venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend in a second terminal:

```bash
cd /Users/ravibyakod/WORK/SpiderCam/spiderpi-sim-starter/frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173`.

## macOS One-Shot Launcher

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

## More Detail

For architecture notes and endpoint details, see `spiderpi-sim-starter/README.md`.
