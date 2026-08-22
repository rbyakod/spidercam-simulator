# SpiderCAM Calibration Checklist

## Pre-Calibration Checks
- [ ] Frame is level (use spirit level on extrusions)
- [ ] All 4 motor mounts firmly bolted
- [ ] All spools secure and run true
- [ ] Cables properly terminated at camera mount
- [ ] All cables similar tension by hand
- [ ] Limit switches tested and functional
- [ ] Backend running (check /health endpoint)
- [ ] UI connected (WebSocket status: Live)

## Step 1: Homing
- [ ] Click "Run Homing Sequence"
- [ ] All 4 axes show "Homed" badge
- [ ] No fault indicators active

## Step 2: Move to Reference Position
- [ ] Target: X=0.5, Y=0.5, Z=0.5
- [ ] All cables visually taut after move

## Step 3: Measure Cable Lengths
- [ ] FL cable: _______ metres
- [ ] FR cable: _______ metres
- [ ] RL cable: _______ metres
- [ ] RR cable: _______ metres

## Step 4: Enter Measurements
- [ ] Open Calibration panel in UI
- [ ] Click "Compute Offsets"
- [ ] Offsets displayed (should be < 50mm each)

## Step 5: Verify
- [ ] Move to X=0.2, Y=0.8, Z=0.2
- [ ] Measure cables and compare to Telemetry
- [ ] Error should be < 5mm on all cables
