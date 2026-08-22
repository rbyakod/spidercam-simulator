# SpiderPi Real Hardware Bring-up Guide

## Prerequisites

Raspberry Pi 4B with Raspberry Pi OS (64-bit recommended).
All hardware assembled per BUILD_GUIDE.md.
MacBook with simulator tested and working.

## Stage 1: Pi Setup

Run on Raspberry Pi:
    sudo apt update
    sudo apt install -y python3-pip python3-venv pigpio
    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod
    systemctl status pigpiod

## Stage 2: Deploy Backend

    cd ~/spiderpi-sim/backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    SPIDERPI_SIM_GPIO=1 uvicorn main:app --host 0.0.0.0 --port 8000

## Stage 3: Verify API from MacBook

    curl http://PI_IP:8000/state
    curl http://PI_IP:8000/switches

## Stage 4: Enable Real GPIO

First disconnect all but motor A. Set low max_freq_hz (800) in config.
    SPIDERPI_SIM_GPIO=0 uvicorn main:app --host 0.0.0.0 --port 8000

## Stage 5: Staged Motor Testing

1. Motor A only: verify direction, step count, limit switch
2. Motor B only: same verification
3. Motor C only: same verification
4. Motor D only: same verification
5. A+C diagonal pair: synchronized move test
6. B+D diagonal pair: synchronized move test
7. All four: slow center move

## Stage 6: Calibration Sequence

Follow CALIBRATION_CHECKLIST.md step by step.
Use the dashboard Calibration Wizard panel.

## Troubleshooting

Motor does not move: check EN pin pulled low, check GPIO 6 output.
Motor wrong direction: toggle invert_dir in config or wizard.
Motor skips steps: reduce max_freq_hz or increase VREF slightly.
Limit switch false triggers: add 100nF hardware debounce capacitor.
pigpio error: run sudo systemctl start pigpiod.
WebSocket drops: use Ethernet instead of Wi-Fi when possible.
