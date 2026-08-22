# Example GPIO pin mapping for Raspberry Pi 4
# Connect DRV8825 STEP/DIR/EN to these BCM GPIO pins
GPIO_MAP = {
    "A": {"step": 12, "dir": 5,  "en": 6},   # Winch A - Front Left
    "B": {"step": 13, "dir": 16, "en": 6},   # Winch B - Front Right
    "C": {"step": 19, "dir": 20, "en": 6},   # Winch C - Rear Right
    "D": {"step": 26, "dir": 21, "en": 6},   # Winch D - Rear Left
}

# Limit switch GPIO pins (BCM numbering, use pull-up)
LIMIT_SWITCH_MAP = {
    "A": 17,
    "B": 27,
    "C": 22,
    "D": 23,
}

# E-stop button GPIO pin
ESTOP_PIN = 24

# Power notes:
# - Pi GPIO -> STEP/DIR/EN on DRV8825 (3.3V logic)
# - External 12V/24V PSU -> VMOT on each DRV8825
# - Shared ground between Pi and motor PSU
# - DO NOT power motors from Pi 5V/3.3V rails
