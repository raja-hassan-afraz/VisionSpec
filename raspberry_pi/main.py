"""VisionSpec: speak nearby obstacles and detected objects."""
import argparse
import subprocess
import time

import cv2

from detector import Detector
from sensors import SensorReader


def direction(centre_x):
    if centre_x < 0.33:
        return "on your left"
    if centre_x > 0.66:
        return "on your right"
    return "ahead"


def build_message(reading, detections, warn_cm):
    """Sensor warnings come first because they are the most urgent."""
    if reading is None:
        return "Distance sensors not responding"
    close = [(cm, side) for side, cm in reading.items() if cm is not None and cm <= warn_cm]
    if close:
        cm, side = min(close)
        where = "ahead" if side == "front" else f"on your {side}"
        return f"Obstacle {where}, {cm} centimetres"
    if detections:
        label, _, centre_x = detections[0]
        return f"{label} {direction(centre_x)}"
    return None


def speak(text):
    return subprocess.Popen(["espeak", "-s", "165", text],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="path to a .tflite model")
    parser.add_argument("--labels", help="text file with one class name per line")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Arduino serial port")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--warn-cm", type=int, default=80)
    parser.add_argument("--repeat-seconds", type=float, default=3.0)
    args = parser.parse_args()

    detector = Detector(args.model, args.labels)
    sensors = SensorReader(args.port)
    sensors.start()
    camera = cv2.VideoCapture(args.camera)
    if not camera.isOpened():
        raise SystemExit("Could not open the camera.")

    voice = None
    last_message, last_time = None, 0.0
    time.sleep(2)  # the Arduino restarts when the serial port opens
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                speak("Camera not responding").wait()
                break
            message = build_message(sensors.latest(), detector.detect(frame), args.warn_cm)
            now = time.monotonic()
            busy = voice is not None and voice.poll() is None
            due = message != last_message or now - last_time >= args.repeat_seconds
            if message and due and not busy:
                print(message)
                voice = speak(message)
                last_message, last_time = message, now
    except KeyboardInterrupt:
        pass
    finally:
        camera.release()


if __name__ == "__main__":
    main()
