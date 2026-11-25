"""Read distance lines sent by the Arduino."""
import threading
import time

import serial

NAMES = ("left", "front", "right")
STALE_AFTER_S = 1.0


def parse_line(line):
    """Turn 'left,front,right' into a dict, or None if the line is invalid."""
    parts = line.strip().split(",")
    if len(parts) != len(NAMES):
        return None
    try:
        values = [int(p) for p in parts]
    except ValueError:
        return None
    return {name: (v if v > 0 else None) for name, v in zip(NAMES, values)}


class SensorReader(threading.Thread):
    """Keeps the latest reading available without blocking the camera loop."""

    def __init__(self, port, baud=115200):
        super().__init__(daemon=True)
        self._serial = serial.Serial(port, baud, timeout=1)
        self._lock = threading.Lock()
        self._reading = None
        self._time = 0.0

    def run(self):
        while True:
            try:
                line = self._serial.readline().decode("ascii", errors="ignore")
            except serial.SerialException:
                return
            reading = parse_line(line)
            if reading:
                with self._lock:
                    self._reading = reading
                    self._time = time.monotonic()

    def latest(self):
        """Return the newest reading, or None if the data is old or missing."""
        with self._lock:
            if time.monotonic() - self._time > STALE_AFTER_S:
                return None
            return self._reading
