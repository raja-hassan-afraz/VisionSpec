# VisionSpec

Wearable assistive navigation smart-glasses prototype for the visually impaired using Raspberry Pi 4, Arduino Uno, HC-SR04 ultrasonic sensors, and real-time TFLite YOLO object detection.

## How it works

1. The Arduino reads three HC-SR04 sensors (left, front, right) and sends the distances over USB serial.
2. The Raspberry Pi reads the camera and runs a YOLOv8 TFLite model.
3. The Pi speaks one message at a time. A close obstacle takes priority over a detected object.

## Hardware

- Raspberry Pi 4
- Arduino Uno, connected to the Pi by USB
- 3 x HC-SR04 ultrasonic sensors
- USB camera
- Earphone or speaker

## Wiring

| Sensor | TRIG | ECHO | VCC | GND |
| --- | --- | --- | --- | --- |
| Left | D2 | D3 | 5V | GND |
| Front | D4 | D5 | 5V | GND |
| Right | D6 | D7 | 5V | GND |

The three-sensor layout and pin numbers are defaults chosen for this code. Change them in the sketch to match your build.

## Setup

1. Upload `arduino/ultrasonic_sensors/ultrasonic_sensors.ino` to the Uno with the Arduino IDE.
2. On the Raspberry Pi (64-bit Raspberry Pi OS):
   ```bash
   sudo apt install espeak
   python3 -m venv venv
   source venv/bin/activate
   pip install -r raspberry_pi/requirements.txt
   ```
3. Export a float32 model on a computer with Ultralytics installed, then copy the `.tflite` file to the Pi:
   ```bash
   yolo export model=yolov8n.pt format=tflite
   ```
   Model files are not included. Check the Ultralytics license before using or sharing a model.
4. Run:
   ```bash
   python raspberry_pi/main.py --model yolov8n_float32.tflite --labels labels.txt
   ```
   `labels.txt` holds one class name per line, in the model's class order. Without it, detections are announced as "object".

## Options

| Option | Default | Meaning |
| --- | --- | --- |
| `--port` | `/dev/ttyACM0` | Arduino serial port |
| `--camera` | `0` | Camera index |
| `--warn-cm` | `80` | Distance that triggers an obstacle warning |
| `--repeat-seconds` | `3.0` | How often the same message repeats |

## Project layout

```
arduino/ultrasonic_sensors/   Arduino sketch
raspberry_pi/main.py          Main loop and spoken messages
raspberry_pi/detector.py      TFLite YOLO detection
raspberry_pi/sensors.py       Serial reader
```
