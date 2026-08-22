# SpiderCAM Manufacturing Release Checklist

## CAD Files
- [ ] spool_v1_direct_5mm.scad - ready to print
- [ ] spool_v1_coupler.scad - ready to print
- [ ] corner_motor_mount_v1.scad - ready to print

## Bill of Materials
- [ ] BOM_INDIA.csv - verified pricing
- [ ] BOM_US.csv - verified pricing
- [ ] BOM_REGIONAL.md - regional alternatives documented

## Software
- [ ] Backend: all Python files present and syntax-checked
- [ ] Frontend: package.json versions pinned
- [ ] Docker: both Dockerfiles tested
- [ ] Simulator mode tested
- [ ] Hardware mode tested on RPi 4B

## Test Results
- [ ] Sim mode: all endpoints responding
- [ ] WebSocket telemetry: 50Hz stable
- [ ] Move command: smooth trapezoidal profile
- [ ] Homing: completes without fault
- [ ] Path playback: square, diagonal paths tested

## Sign-Off
- Reviewed by: _______________ Date: _______________
