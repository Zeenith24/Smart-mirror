"""
Magic Mirror AI - Main Orchestrator
Pub/Mall Installation Version

Flow:
  Proximity trigger → Camera capture → Face detection →
  Interaction engine → Text-to-speech → Audio output
"""

import time
import logging
import sys
from pathlib import Path

from camera import Camera
from face_detector import FaceDetector
from interaction_engine import InteractionEngine
from tts_engine import TTSEngine
from proximity import ProximitySensor
from overlay import OverlayDisplay
from speech_recognition_engine import SpeechRecognitionEngine
from config_loader import load_config

# ── Logging ──
LOG_PATH = Path("logs/mirror.log")
LOG_PATH.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("main")


def run():
    log.info("═" * 60)
    log.info("  Magic Mirror AI — Starting Up")
    log.info("═" * 60)

    cfg = load_config("config/settings.yaml")

    camera    = Camera(device_index=cfg["camera"]["device_index"])
    detector  = FaceDetector(cfg["face_detection"])
    engine    = InteractionEngine(cfg["interaction"])
    tts       = TTSEngine(cfg["tts"])
    proximity = ProximitySensor(cfg["proximity"])
    overlay   = OverlayDisplay(cfg["overlay"])
    speech    = SpeechRecognitionEngine(cfg["speech_recognition"])

    log.info("All subsystems ready. Entering main loop.")

    try:
        while True:
            # Step 1: Wait for approach
            if not proximity.is_triggered():
                time.sleep(0.1)
                continue

            log.info("Proximity triggered — capturing frame")

            # Step 2: Grab frame
            frame = camera.capture()
            if frame is None:
                log.warning("Camera returned no frame — skipping")
                time.sleep(0.5)
                continue

            # Step 3: Detect faces
            faces = detector.detect(frame)
            face_count = len(faces)
            log.info(f"Detected {face_count} face(s)")

            if face_count == 0:
                time.sleep(0.2)
                continue

            # Step 4: Get line and speak
            line = engine.get_line(face_count)
            if line:
                log.info(f"Speaking: {line!r}")
                overlay.show(line, face_count)
                tts.speak(line)
                
                # Step 4b: Listen for user response (if speech recognition enabled)
                if speech.enabled:
                    user_text = speech.listen()
                    if user_text:
                        # User responded — generate a reply and speak it
                        response = engine.get_response(user_text)
                        log.info(f"User said: {user_text!r}")
                        log.info(f"Responding: {response!r}")
                        overlay.show(response, face_count)
                        tts.speak(response)
                    else:
                        log.info("User didn't respond or speech unclear — ending interaction")
            else:
                log.info("Engine in cooldown — staying quiet")
                # Step 4c: Mandatory 5-second pause to let person move away
                log.info("Waiting 5 seconds for person to move away...")
                time.sleep(5.0)
            # Step 5: Brief pause before next trigger check
            time.sleep(cfg["interaction"]["post_speak_pause"])

    except KeyboardInterrupt:
        log.info("Shutdown requested — goodbye!")
    finally:
        camera.release()
        overlay.close()
        log.info("Clean shutdown complete.")


if __name__ == "__main__":
    run()
