"""
tts_engine.py — Text-to-Speech with multiple backend support.

Backends:
  pyttsx3    — 100% offline, uses Windows SAPI voices. Works out of the box.
  edge-tts   — Microsoft neural voices via internet. Much more natural.
               Requires: pip install edge-tts  +  internet connection.
  gtts       — Google TTS via internet. Simple fallback.
               Requires: pip install gtts playsound
"""

import logging
import threading
import tempfile
import os

log = logging.getLogger("tts_engine")


class TTSEngine:
    def __init__(self, cfg: dict):
        self.backend     = cfg.get("engine", "pyttsx3")
        self.rate        = cfg.get("rate", 170)
        self.volume      = cfg.get("volume", 1.0)
        self.voice_index = cfg.get("voice_index", 0)
        self.edge_voice  = cfg.get("edge_voice", "en-GB-RyanNeural")

        self._engine = None
        self._init_backend()

    # ── Init ──

    def _init_backend(self):
        if self.backend == "pyttsx3":
            self._init_pyttsx3()
        elif self.backend == "edge-tts":
            self._check_edge_tts()
        elif self.backend == "gtts":
            self._check_gtts()
        else:
            log.warning(f"Unknown TTS backend '{self.backend}' — falling back to pyttsx3")
            self.backend = "pyttsx3"
            self._init_pyttsx3()

    def _init_pyttsx3(self):
        try:
            import pyttsx3
            # Verify it can init and log available voices.
            # We do NOT keep a persistent engine — Windows COM breaks on reuse.
            # A fresh engine is spun up in its own thread for every speak() call.
            probe = pyttsx3.init()
            voices = probe.getProperty("voices")
            if voices and self.voice_index < len(voices):
                log.info(f"pyttsx3 voice [{self.voice_index}]: {voices[self.voice_index].name}")
            else:
                log.info(f"pyttsx3 ready — {len(voices or [])} voice(s) found")
            probe.stop()
            log.info("pyttsx3 TTS ready (offline, fresh-thread mode)")
        except ImportError:
            log.error("pyttsx3 not installed. Run: pip install pyttsx3")
            raise

    def _check_edge_tts(self):
        try:
            import edge_tts  # noqa: F401
            import asyncio   # noqa: F401
            log.info(f"edge-tts ready, voice={self.edge_voice}")
        except ImportError:
            log.error("edge-tts not installed. Run: pip install edge-tts")
            raise

    def _check_gtts(self):
        try:
            from gtts import gTTS  # noqa: F401
            import playsound        # noqa: F401
            log.info("gTTS ready")
        except ImportError:
            log.error("gtts/playsound not installed. Run: pip install gtts playsound")
            raise

    # ── Speak ─

    def speak(self, text: str):
        """Speak text — blocks until done."""
        log.debug(f"TTS speak: {text!r}")
        if self.backend == "pyttsx3":
            self._speak_pyttsx3(text)
        elif self.backend == "edge-tts":
            self._speak_edge_tts(text)
        elif self.backend == "gtts":
            self._speak_gtts(text)

    def _speak_pyttsx3(self, text: str):
        """
        Windows fix: pyttsx3's COM event loop breaks silently after the first
        runAndWait() call when reused on the same thread. The reliable workaround
        is to init a fresh engine instance in a new thread for every utterance.
        The thread is joined so speak() still blocks until audio finishes.
        """
        import threading
        import pyttsx3

        error_holder = []

        def _worker():
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", self.rate)
                engine.setProperty("volume", self.volume)
                voices = engine.getProperty("voices")
                if voices and self.voice_index < len(voices):
                    engine.setProperty("voice", voices[self.voice_index].id)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                error_holder.append(e)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        t.join(timeout=15)          # safety timeout — never hangs the main loop

        if error_holder:
            log.error(f"pyttsx3 error: {error_holder[0]}")
        elif t.is_alive():
            log.warning("pyttsx3 thread timed out — skipping this utterance")

    def _speak_edge_tts(self, text: str):
        """edge-tts is async — run in event loop, save mp3, play it."""
        import asyncio
        import edge_tts

        async def _gen():
            communicate = edge_tts.Communicate(text, self.edge_voice)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp = f.name
            await communicate.save(tmp)
            return tmp

        try:
            tmp_path = asyncio.run(_gen())
            self._play_file(tmp_path)
        except Exception as e:
            log.error(f"edge-tts error: {e}")
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def _speak_gtts(self, text: str):
        from gtts import gTTS
        try:
            tts = gTTS(text=text, lang="en", tld="co.uk")
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp = f.name
            tts.save(tmp)
            self._play_file(tmp)
        except Exception as e:
            log.error(f"gTTS error: {e}")
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    def _play_file(self, path: str):
        """Play an audio file — uses pygame for reliability on Windows."""
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                import time
                time.sleep(0.05)
        except ImportError:
            # Fallback: playsound
            try:
                from playsound import playsound
                playsound(path)
            except ImportError:
                log.error("Neither pygame nor playsound available. Run: pip install pygame")
