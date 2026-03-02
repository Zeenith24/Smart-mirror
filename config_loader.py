"""
config_loader.py — Loads and validates settings.yaml
Falls back to sensible defaults if a key is missing.
"""

import yaml
import logging
from pathlib import Path

log = logging.getLogger("config_loader")

DEFAULTS = {
    "camera": {
        "device_index": 0,
    },
    "face_detection": {
        "scale_factor": 1.1,
        "min_neighbors": 5,
        "min_face_size": 80,
    },
    "proximity": {
        "mode": "motion",           # "motion" | "always_on" | "gpio" | "http"
        "motion_threshold": 1500,   # pixel diff threshold for motion mode
        "cooldown_seconds": 2.0,
    },
    "interaction": {
        "cooldown_seconds": 10.0,
        "max_repeats_before_shuffle": 3,
        "post_speak_pause": 2.0,
        "tone": "mixed",       # "pub_banter" | "welcoming" | "mysterious" | "cheeky"
    },
    "tts": {
        "engine": "edge-tts",        # "pyttsx3" | "edge-tts" | "gtts"
        "rate": 170,
        "volume": 1.0,
        "voice_index": 0,
        "edge_voice": "en-GB-RyanNeural",
    },
    "overlay": {
        "enabled": True,
        "fullscreen": False,
        "font_size": 48,
        "bg_color": [0, 0, 0],
        "text_color": [255, 215, 0],
    },
    "speech_recognition": {
        "enabled": True,
        "listen_timeout": 5.0,
        "phrase_timeout": 3.0,
        "ambient_adjust": 1.0,
    },
}


def deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, recursively."""
    result = base.copy()
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load_config(path: str = "config/settings.yaml") -> dict:
    cfg_path = Path(path)
    if not cfg_path.exists():
        log.warning(f"Config file not found at {path} — using all defaults")
        return DEFAULTS

    with open(cfg_path, "r", encoding="utf-8") as f:
        user_cfg = yaml.safe_load(f) or {}

    merged = deep_merge(DEFAULTS, user_cfg)
    log.info(f"Config loaded from {path}")
    return merged
