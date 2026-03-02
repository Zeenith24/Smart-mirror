"""
test_components.py — Sanity-check each subsystem independently.
Run this first to make sure everything is installed correctly.

Usage:
  python test_components.py
  python test_components.py --skip-tts   (if no speaker connected)
"""

import sys
import argparse
import time

PASS = "  correct ✓"
FAIL = "  wrong ✗"
SKIP = "  –"

def section(name):
    print(f"\n{'─'*50}")
    print(f"  {name}")
    print('─'*50)


def test_imports():
    section("1. Checking required packages")
    packages = {
        "cv2":      "opencv-python",
        "numpy":    "numpy",
        "yaml":     "pyyaml",
        "pyttsx3":  "pyttsx3",
        "pygame":   "pygame",
    }
    all_ok = True
    for mod, pip_name in packages.items():
        try:
            __import__(mod)
            print(f"{PASS} {mod}")
        except ImportError:
            print(f"{FAIL} {mod}  →  run: pip install {pip_name}")
            all_ok = False
    return all_ok


def test_camera():
    section("2. Camera")
    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print(f"{FAIL} Could not open camera 0")
            return False
        ret, frame = cap.read()
        cap.release()
        if ret and frame is not None:
            print(f"{PASS} Camera opened and captured a frame ({frame.shape[1]}x{frame.shape[0]})")
            return True
        else:
            print(f"{FAIL} Camera opened but returned no frame")
            return False
    except Exception as e:
        print(f"{FAIL} Camera error: {e}")
        return False


def test_face_detection():
    section("3. Face Detection (Haar Cascade)")
    try:
        import cv2
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        clf = cv2.CascadeClassifier(cascade_path)
        if clf.empty():
            print(f"{FAIL} Cascade classifier is empty")
            return False
        print(f"{PASS} haarcascade_frontalface_default.xml loaded")
        print(f"      Path: {cascade_path}")
        return True
    except Exception as e:
        print(f"{FAIL} Face detection error: {e}")
        return False


def test_tts(skip: bool = False):
    section("4. Text-to-Speech (pyttsx3)")
    if skip:
        print(f"{SKIP} Skipped (--skip-tts flag)")
        return True
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        print(f"{PASS} pyttsx3 initialised — {len(voices)} voice(s) available")
        for i, v in enumerate(voices[:3]):
            print(f"       [{i}] {v.name}")
        engine.say("Magic mirror, ready to go.")
        engine.runAndWait()
        print(f"{PASS} TTS spoke successfully")
        return True
    except Exception as e:
        print(f"{FAIL} TTS error: {e}")
        return False


def test_config():
    section("5. Config loader")
    try:
        sys.path.insert(0, ".")
        from config_loader import load_config
        cfg = load_config("config/settings.yaml")
        print(f"{PASS} Config loaded")
        print(f"       Tone:      {cfg['interaction']['tone']}")
        print(f"       TTS:       {cfg['tts']['engine']}")
        print(f"       Proximity: {cfg['proximity']['mode']}")
        return True
    except Exception as e:
        print(f"{FAIL} Config error: {e}")
        return False


def test_interaction_engine():
    section("6. Interaction Engine")
    try:
        sys.path.insert(0, ".")
        from interaction_engine import InteractionEngine
        engine = InteractionEngine({
            "cooldown_seconds": 0,
            "max_repeats_before_shuffle": 3,
            "tone": "pub_banter",
        })
        solo_line  = engine.get_line(1)
        group_line = engine.get_line(2)
        print(f"{PASS} Solo line:  {solo_line!r}")
        print(f"{PASS} Group line: {group_line!r}")
        return True
    except Exception as e:
        print(f"{FAIL} Interaction engine error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-tts", action="store_true", help="Skip TTS test (no speaker)")
    args = parser.parse_args()

    print("\n" + "═"*50)
    print("  Magic Mirror AI — Component Test")
    print("═"*50)

    results = [
        test_imports(),
        test_camera(),
        test_face_detection(),
        test_tts(skip=args.skip_tts),
        test_config(),
        test_interaction_engine(),
    ]

    print("\n" + "═"*50)
    passed = sum(results)
    total  = len(results)
    if passed == total:
        print(f"  All {total} tests passed. Ready to run: python main.py")
    else:
        print(f"  {passed}/{total} tests passed. Fix the issues above, then run again.")
    print("═"*50 + "\n")


if __name__ == "__main__":
    main()
