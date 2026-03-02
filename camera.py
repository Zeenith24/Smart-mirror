"""
camera.py — Webcam capture using OpenCV.
Handles device open/close and frame grabs gracefully.
"""

import cv2
import logging

log = logging.getLogger("camera")


class Camera:
    def __init__(self, device_index: int = 0):
        self.device_index = device_index
        self._cap = None
        self._open()

    def _open(self):
        log.info(f"Opening camera device {self.device_index}")
        self._cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)  # CAP_DSHOW = Windows optimised
        if not self._cap.isOpened():
            log.error(f"Could not open camera {self.device_index}. Check it is connected and not in use.")
            raise RuntimeError(f"Camera {self.device_index} unavailable")

        # Prefer a reasonable resolution — fast but enough for face detection
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self._cap.set(cv2.CAP_PROP_FPS, 15)
        log.info("Camera ready")

    def capture(self):
        """Return a single BGR frame, or None on failure."""
        if not self._cap or not self._cap.isOpened():
            log.warning("Camera not open — attempting reopen")
            try:
                self._open()
            except RuntimeError:
                return None

        # Flush stale buffered frames (common on Windows)
        for _ in range(3):
            self._cap.grab()

        ret, frame = self._cap.read()
        if not ret or frame is None:
            log.warning("Failed to read frame from camera")
            return None
        return frame

    def release(self):
        if self._cap:
            self._cap.release()
            log.info("Camera released")
