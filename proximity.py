"""
proximity.py — Proximity / trigger detection.

Modes:
  motion      — detects movement via frame differencing on the webcam (default).
                No extra hardware needed. Great for laptop/Pi with a camera.
  always_on   — permanently triggered. Useful for testing or busy venues.
  gpio        — reads a GPIO pin (Raspberry Pi only, e.g. PIR sensor).
  http        — waits for an HTTP POST to http://localhost:{port}/trigger.
                Lets an external sensor/microcontroller fire the mirror.
"""

import time
import threading
import logging
import numpy as np

log = logging.getLogger("proximity")


class ProximitySensor:
    def __init__(self, cfg: dict):
        self.mode             = cfg.get("mode", "motion")
        self.motion_threshold = cfg.get("motion_threshold", 1500)
        self.cooldown_seconds = cfg.get("cooldown_seconds", 2.0)

        self._triggered       = False
        self._last_trigger_at = 0.0
        self._prev_frame      = None

        # Mode-specific setup
        if self.mode == "motion":
            log.info("Proximity: motion detection mode (camera-based)")
        elif self.mode == "always_on":
            log.info("Proximity: always-on mode — will always trigger")
        elif self.mode == "gpio":
            self._gpio_pin = cfg.get("gpio_pin", 17)
            self._setup_gpio()
        elif self.mode == "http":
            self._http_port = cfg.get("http_port", 8765)
            self._start_http_listener()
        else:
            log.warning(f"Unknown proximity mode '{self.mode}' — falling back to motion")
            self.mode = "motion"

    # ── Public API ──

    def is_triggered(self, frame: np.ndarray = None) -> bool:
        """
        Returns True if proximity is detected.
        For 'motion' mode, pass in the current camera frame.
        main.py handles passing the frame; for other modes frame is ignored.
        """
        if self.mode == "always_on":
            return True

        if self.mode in ("gpio", "http"):
            return self._check_with_cooldown(self._triggered)

        if self.mode == "motion" and frame is not None:
            return self._check_motion(frame)

        # motion mode but no frame passed — signal main to get one first
        return True  # main.py will capture frame then re-evaluate via detect()

    def notify_triggered(self):
        """External call — e.g. from HTTP listener or GPIO callback."""
        self._triggered = True

    # ── Motion Detection mode ───

    def _check_motion(self, frame: np.ndarray) -> bool:
        import cv2

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self._prev_frame is None:
            self._prev_frame = gray
            return False

        delta = cv2.absdiff(self._prev_frame, gray)
        _, thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)
        motion_score = np.sum(thresh)

        self._prev_frame = gray

        if motion_score > self.motion_threshold:
            return self._check_with_cooldown(True)
        return False

    # ── GPIO (Pi) ───

    def _setup_gpio(self):
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._gpio_pin, GPIO.IN)
            GPIO.add_event_detect(
                self._gpio_pin,
                GPIO.RISING,
                callback=lambda _: self.notify_triggered(),
                bouncetime=300,
            )
            log.info(f"GPIO ready on pin {self._gpio_pin}")
        except ImportError:
            log.warning("RPi.GPIO not available — GPIO mode disabled, switching to motion")
            self.mode = "motion"

    # ── HTTP Listener ──

    def _start_http_listener(self):
        from http.server import HTTPServer, BaseHTTPRequestHandler

        sensor = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                if self.path == "/trigger":
                    sensor.notify_triggered()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"OK")
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, *args):
                pass  # suppress HTTP access logs

        def serve():
            server = HTTPServer(("0.0.0.0", self._http_port), Handler)
            log.info(f"HTTP trigger listener on port {self._http_port}")
            server.serve_forever()

        t = threading.Thread(target=serve, daemon=True)
        t.start()

    # ── Cooldown helper ───

    def _check_with_cooldown(self, raw: bool) -> bool:
        if not raw:
            return False
        now = time.time()
        if now - self._last_trigger_at < self.cooldown_seconds:
            self._triggered = False
            return False
        self._last_trigger_at = now
        self._triggered = False
        return True
