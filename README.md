# Magic Mirror AI 
### Pub/Mall Installation — Setup & Operating Guide


Developed by:Charitha K R (https://github.com/Charitha-kr)  
Hardware Integration: Harshit Ravi

Interactive conversational mirror with AI-powered face detection and speech recognition.

---

## 🏆 Project Attribution

**Software (100%):** [Charitha K R]
- Complete Python application architecture
- AI conversation engine with 190+ dialogue lines
- Computer vision and speech recognition integration
- Multi-platform hardware support framework

**Hardware:** [Harshit Ravi]
- Physical installation and wiring

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for detailed breakdown.

---
** Conversational Mode! 🎤** The mirror can now listen and respond to what people say. See `CONVERSATIONAL_MODE.md` for setup.

---

## What It Does

When someone walks up to the mirror, it:
1. **Detects** them using the webcam
2. **Counts** faces (solo visitor vs. group)
3. **Speaks** a funny, pub-appropriate line through the speaker
4. **Waits** before speaking again (so it doesn't annoy people)

---

## File Structure

```
mirror_ai/
├── main.py                  ← Run this to start the mirror
├── test_components.py       ← Run this first to check everything works
├── START_MIRROR.bat         ← Double-click to start (and auto-restart if it crashes)
│
├── camera.py                ← Webcam handling
├── face_detector.py         ← Face counting
├── interaction_engine.py    ← All the dialogue lines + timing logic + conversational responses
├── tts_engine.py            ← Text-to-speech
├── speech_recognition_engine.py  ← Listens to user responses (NEW!)
├── proximity.py             ← Motion detection (no extra hardware needed)
├── overlay.py               ← On-screen text display
├── config_loader.py         ← Reads settings.yaml
│
├── config/
│   └── settings.yaml        ← ALL settings live here — edit this to customise
│
├── logs/
│   └── mirror.log           ← Auto-generated log file for troubleshooting
│
├── CONVERSATIONAL_MODE.md   ← How to set up two-way conversations (NEW!)
└── requirements.txt         ← Python packages to install
```

---

## Step 1 — Install Python

Download Python 3.11 from: https://www.python.org/downloads/

>  On the installer, tick **"Add Python to PATH"** before clicking Install.

---

## Step 2 — Install Dependencies

Open **Command Prompt** in the `mirror_ai` folder and run:

```
pip install -r requirements.txt
```

This installs OpenCV, pyttsx3 (voice), pygame (audio), and PyYAML.

---

## Step 3 — Test Everything

```
python test_components.py
```

You should see all  ticks. If anything fails, it will tell you what to fix.

---

## Step 4 — Run the Mirror

**Option A — Command line:**
```
python main.py
```

**Option B — Double-click:**
Double-click `START_MIRROR.bat` — this also auto-restarts if it crashes.

---

## Step 5 — Make It Start on Boot (for permanent installation)

1. Press `Win + R` → type `shell:startup` → press Enter
2. Copy a **shortcut** to `START_MIRROR.bat` into that folder
3. The mirror will now start automatically every time Windows boots

---

## Customising the Dialogue

Open `config/settings.yaml` and change the **tone**:

| Tone | Style |
|------|-------|
| `pub_banter` | Cheeky, funny — *"You look like you need a pint"* |
| `welcoming`  | Warm and friendly — *"Great to see you!"* |
| `mysterious` | Theatrical — *"The mirror sees all..."* |
| `cheeky`     | Playful — *"The mirror called. It wants you to know you're doing great"* |

To add your own lines, open `interaction_engine.py` and add to the `LINES` dictionary.

---

## Key Settings (`config/settings.yaml`)

| Setting | What It Does |
|---------|-------------|
| `interaction.cooldown_seconds` | How long before it speaks again (default: 10s) |
| `tts.edge_voice` | The voice used (see voice options in settings file) |
| `proximity.motion_threshold` | How much movement triggers it (lower = more sensitive) |
| `overlay.enabled` | Show text on screen (set `false` if no screen) |

---

## Upgrading to a Better Voice (Recommended)

The default voice (`pyttsx3`) uses Windows' built-in robot voices.
For a much more natural British voice:

1. Run: `pip install edge-tts` both in Command prompt and terminal
2. In `settings.yaml`, change: `engine: edge-tts`
3. The voice `en-GB-RyanNeural` sounds great for a pub — like a friendly bloke.

>  This requires an internet connection on the installation machine.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Camera unavailable" | Check another app isn't using the webcam; try `device_index: 1` |
| No sound | Check Windows volume; check speaker is set as default audio output |
| Triggering too easily | Increase `motion_threshold` in settings (e.g. `3000`) |
| Not triggering enough | Decrease `motion_threshold` (e.g. `800`) |
| Same lines repeating | Increase `max_repeats_before_shuffle` or add more lines |

All errors are logged to `logs/mirror.log` — share this file when asking for support.

---

## Hardware Used

- Windows laptop or mini PC
- USB webcam (720p is fine)
- Powered speaker (3.5mm or USB)
- Optional: proximity/PIR sensor wired to a microcontroller

---

## Upgrading to Raspberry Pi

When ready to move to dedicated hardware:
1. Change `cv2.CAP_DSHOW` → `cv2.CAP_V4L2` in `camera.py`
2. Set `proximity.mode: gpio` in `settings.yaml` if using a PIR sensor
3. Set up a systemd service for auto-start instead of the .bat file
4. Everything else stays the same

---


