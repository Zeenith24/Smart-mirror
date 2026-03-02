"""
face_detector.py — Face detection using OpenCV Haar Cascades.
No GPU needed, works offline, fast on a laptop or Pi.
"""

import cv2
import numpy as np
import logging
from pathlib import Path

log = logging.getLogger("face_detector")


class FaceDetector:
    def __init__(self, cfg: dict):
        self.scale_factor  = cfg.get("scale_factor", 1.1)
        self.min_neighbors = cfg.get("min_neighbors", 5)
        self.min_face_size = cfg.get("min_face_size", 80)

        # OpenCV ships with this cascade — no download needed
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if not Path(cascade_path).exists():
            raise FileNotFoundError(f"Haar cascade not found at: {cascade_path}")

        self._cascade = cv2.CascadeClassifier(cascade_path)
        log.info("Face detector ready (Haar cascade)")

    def detect(self, frame: np.ndarray) -> list[tuple]:
        """
        Returns a list of (x, y, w, h) bounding boxes for each detected face.
        Returns [] if no faces found.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)   # improves detection in variable pub lighting

        faces = self._cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=(self.min_face_size, self.min_face_size),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        if len(faces) == 0:
            return []

        return [tuple(f) for f in faces]

    def annotate(self, frame: np.ndarray, faces: list[tuple]) -> np.ndarray:
        """Draw bounding boxes on frame — useful for the overlay/debug view."""
        annotated = frame.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 215, 0), 2)
        return annotated
