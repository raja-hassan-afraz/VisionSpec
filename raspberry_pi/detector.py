"""Object detection with a float32 YOLOv8 TFLite model."""
import cv2
import numpy as np

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    from ai_edge_litert.interpreter import Interpreter


class Detector:
    def __init__(self, model_path, labels_path=None, confidence=0.45, iou=0.5):
        self.interpreter = Interpreter(model_path=model_path, num_threads=4)
        self.interpreter.allocate_tensors()
        self.input = self.interpreter.get_input_details()[0]
        self.output = self.interpreter.get_output_details()[0]
        if self.input["dtype"] != np.float32:
            raise ValueError("Use a float32 TFLite model.")
        _, self.height, self.width, _ = self.input["shape"]
        self.confidence = confidence
        self.iou = iou
        self.labels = []
        if labels_path:
            with open(labels_path, encoding="utf-8") as f:
                self.labels = [line.strip() for line in f]

    def label(self, class_id):
        return self.labels[class_id] if class_id < len(self.labels) else "object"

    def detect(self, frame):
        """Return a list of (label, score, centre_x), with centre_x from 0 to 1."""
        image = cv2.cvtColor(cv2.resize(frame, (int(self.width), int(self.height))), cv2.COLOR_BGR2RGB)
        tensor = np.expand_dims(image.astype(np.float32) / 255.0, axis=0)
        self.interpreter.set_tensor(self.input["index"], tensor)
        self.interpreter.invoke()

        # YOLOv8 output shape: (1, 4 + classes, boxes)
        rows = self.interpreter.get_tensor(self.output["index"])[0].T
        class_scores = rows[:, 4:]
        class_ids = np.argmax(class_scores, axis=1)
        scores = class_scores[np.arange(len(rows)), class_ids]
        keep = scores >= self.confidence
        if not np.any(keep):
            return []

        boxes = rows[keep, :4].copy()  # centre x, centre y, width, height
        scores, class_ids = scores[keep], class_ids[keep]
        if boxes.max() > 2:  # some exports give pixels instead of 0..1
            boxes[:, [0, 2]] /= self.width
            boxes[:, [1, 3]] /= self.height

        pixel_boxes = [
            [float((x - w / 2) * self.width), float((y - h / 2) * self.height),
             float(w * self.width), float(h * self.height)]
            for x, y, w, h in boxes
        ]
        chosen = cv2.dnn.NMSBoxes(pixel_boxes, scores.tolist(), self.confidence, self.iou)
        results = [
            (self.label(int(class_ids[i])), float(scores[i]), float(boxes[i, 0]))
            for i in np.array(chosen).flatten()
        ]
        return sorted(results, key=lambda r: r[1], reverse=True)
