# VisionSpec

Wearable assistive navigation smart-glasses prototype for the visually impaired using Raspberry Pi 4, Arduino Uno, HC-SR04 ultrasonic sensors, and real-time TFLite YOLO object detection.

## How it works

1. The Arduino reads three HC-SR04 sensors (left, front, right), applies a **1D Kalman Filter** to stabilize noisy distance readings, and sends the filtered distances over USB serial.
2. The Raspberry Pi reads the camera feed, applies **OpenCV HSV color-space filtering**, and runs a custom-trained **7-class YOLOv8 TFLite model** (annotated and augmented using Roboflow).
3. The Pi speaks one message at a time. A close obstacle takes priority over a detected object.

## Validation & Experimental Results

- **Obstacle Detection Rate:** Achieved an **83% obstacle detection rate** across **60 structured indoor and outdoor trials** conducted with **3 visually impaired participants**.
- **Sensor Stabilization:** Integrating the 1D Kalman Filter significantly reduced false proximity alerts caused by ultrasonic acoustic reflections.
- **Edge Inference:** Deployed a lightweight 7-class TensorFlow Lite object detection model optimized for real-time on-device execution on the Raspberry Pi 4.

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

   Export a float32 model on a computer with Ultralytics installed, then copy the .tflite file to the Pi:
yolo export model=yolov8n.pt format=tflite

Run:

python raspberry_pi/main.py --model yolov8n_float32.tflite --labels labels.txt
labels.txt holds one class name per line, in the model's class order. Without it, detections are announced as "object".

| Option           | Default      | Meaning | 
| --port           | /dev/ttyACM0 | Arduino serial port |
| --camera         | 0            | Camera index |
| --warn-cm        | 80           | Distance that triggers an obstacle warning | 
| --repeat-seconds | 3.0          | How often the same message repeats |

Project layout

arduino/ultrasonic_sensors/ -Arduino sketch
raspberry_pi/main.py - Main loop and spoken messages
raspberry_pi/detector.py - TFLite YOLO detection
raspberry_pi/sensors.py - Serial reader
