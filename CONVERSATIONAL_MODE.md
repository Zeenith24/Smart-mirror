# 🎤 Conversational Mode Setup Guide

Your mirror can now have **two-way conversations**! After it greets someone, it listens for a response and replies back before ending the interaction.

---

## How It Works

1. **Mirror speaks** → *"You look like you need a pint. Am I wrong?"*
2. **Person responds** → *"Yeah, I do!"* or *"Hello!"* or *"Who are you?"*
3. **Mirror replies** → *"Right back at you! Now go enjoy the pub."*
4. **Conversation ends** — mirror goes back to waiting mode

---

## Installation (Windows)

### Step 1 — Install PyAudio (microphone support)

PyAudio needs a manual install on Windows. Download the correct wheel file for your Python version:

**Python 3.11 (64-bit)** — most common:
```
pip install https://github.com/intxcc/pyaudio_portaudio/releases/download/v19.7.0/PyAudio-0.2.13-cp311-cp311-win_amd64.whl
```

**Python 3.10 (64-bit):**
```
pip install https://github.com/intxcc/pyaudio_portaudio/releases/download/v19.7.0/PyAudio-0.2.13-cp310-cp310-win_amd64.whl
```

**Python 3.12 (64-bit):**
```
pip install https://github.com/intxcc/pyaudio_portaudio/releases/download/v19.7.0/PyAudio-0.2.13-cp312-cp312-win_amd64.whl
```

If you're not sure which Python version you have, run: `python --version`

### Step 2 — Install speech recognition

```
pip install SpeechRecognition
```

### Step 3 — Test your microphone

Run the mirror and watch the console logs. You should see:
```
Calibrating microphone for ambient noise...
Speech recognition ready (timeout=5.0s)
```

If you see errors about the microphone, check:
- Your microphone is plugged in and set as the **default recording device** in Windows Sound Settings
- No other app is using the microphone

---

## How to Use

The mirror automatically listens for 5 seconds after it speaks. If the person says something, it responds. If they don't, the interaction ends naturally.

**Example conversations:**

| Person says | Mirror responds |
|-------------|-----------------|
| *"Hello!"* | *"Cheers! Have a great one."* |
| *"Thanks!"* | *"Pleasure's all mine. Off you go!"* |
| *"Who are you?"* | *"I'm the magic mirror. Been watching this place for years."* |
| *"You're cool!"* | *"Right back at you! Now go enjoy the pub."* |
| *(silence)* | *(no response, interaction ends)* |

---

## Disable Conversational Mode

If you want the mirror to just greet people without waiting for responses, edit `config/settings.yaml`:

```yaml
speech_recognition:
  enabled: false
```

Then restart the mirror. It will speak but not listen.

---

## Tuning for Noisy Pubs

If the mirror is picking up too much background noise or struggling to hear:

**In `config/settings.yaml`:**

```yaml
speech_recognition:
  listen_timeout: 5.0      # ⬆ Increase to 7.0 if people speak slowly
  phrase_timeout: 3.0      # ⬇ Decrease to 2.0 if picking up too much noise
  ambient_adjust: 1.0      # ⬆ Increase to 2.0 for very noisy pubs
```

- **listen_timeout** — how long to wait for someone to START speaking
- **phrase_timeout** — how much silence = "they're done talking"
- **ambient_adjust** — how long to calibrate for background noise on startup

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Microphone initialization failed" | Check mic is plugged in and set as default device in Windows |
| "PyAudio not installed" | Follow Step 1 above — install the wheel file |
| Mirror hears everything as noise | Increase `ambient_adjust` to 2.0 |
| Mirror doesn't respond to speech | Check Windows volume/mic isn't muted; try speaking louder/closer |
| "Speech detected but couldn't understand" | Too noisy or person spoke unclearly — this is normal in pubs |

---

## How Google Speech Recognition Works

The mirror uses **Google's free speech-to-text API** (no API key needed). When someone speaks:

1. Records audio for up to 5 seconds
2. Sends it to Google's servers
3. Gets back the text transcription
4. Generates a contextual response

**This requires an internet connection on the installation machine.**

If you need 100% offline mode, set `speech_recognition.enabled: false` in the config.

---

*Now the mirror can actually chat back! 🎤*
