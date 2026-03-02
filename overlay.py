"""
overlay.py — Optional on-screen display using OpenCV.

Shows the spoken line as text on a window — useful if the mirror
has a screen behind it (e.g. a monitor behind a two-way mirror).
Can be disabled in config if no screen is attached.
"""

import cv2
import numpy as np
import threading
import time
import logging

log = logging.getLogger("overlay")


class OverlayDisplay:
    def __init__(self, cfg: dict):
        self.enabled    = cfg.get("enabled", True)
        self.fullscreen = cfg.get("fullscreen", False)
        self.font_size  = cfg.get("font_size", 48)
        self.bg_color   = tuple(cfg.get("bg_color", [0, 0, 0]))
        self.text_color = tuple(cfg.get("text_color", [255, 215, 0]))  # gold

        self._win_name  = "Magic Mirror"
        self._current_text = ""
        self._show_until   = 0.0
        self._lock         = threading.Lock()
        self._thread       = None
        self._running      = False

        if self.enabled:
            self._start()

    def _start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        log.info("Overlay display started")

    def _loop(self):
        cv2.namedWindow(self._win_name, cv2.WINDOW_NORMAL)
        if self.fullscreen:
            cv2.setWindowProperty(self._win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.resizeWindow(self._win_name, 800, 300)

        while self._running:
            with self._lock:
                text       = self._current_text
                show_until = self._show_until

            canvas = self._render(text if time.time() < show_until else "")
            cv2.imshow(self._win_name, canvas)

            key = cv2.waitKey(50)
            if key == 27:  # ESC to close overlay
                break

        cv2.destroyAllWindows()

    def _render(self, text: str) -> np.ndarray:
        h, w = 300, 800
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        canvas[:] = self.bg_color

        if not text:
            return canvas

        font       = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        thickness  = 2
        max_width  = w - 40

        # Word-wrap
        words  = text.split()
        lines  = []
        line   = ""
        for word in words:
            test = f"{line} {word}".strip()
            (tw, _), _ = cv2.getTextSize(test, font, font_scale, thickness)
            if tw > max_width and line:
                lines.append(line)
                line = word
            else:
                line = test
        if line:
            lines.append(line)

        # Draw lines centred
        (_, line_h), baseline = cv2.getTextSize("A", font, font_scale, thickness)
        total_h = len(lines) * (line_h + 10)
        y = (h - total_h) // 2 + line_h

        for l in lines:
            (tw, _), _ = cv2.getTextSize(l, font, font_scale, thickness)
            x = (w - tw) // 2
            cv2.putText(canvas, l, (x, y), font, font_scale, self.text_color, thickness, cv2.LINE_AA)
            y += line_h + 10

        return canvas

    def show(self, text: str, face_count: int = 1, duration: float = 6.0):
        """Display text on the overlay for `duration` seconds."""
        if not self.enabled:
            return
        with self._lock:
            self._current_text = text
            self._show_until   = time.time() + duration

    def close(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        log.info("Overlay closed")
