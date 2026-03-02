"""
speech_recognition_engine.py — Listen for user speech after the mirror speaks.

Uses Google Speech Recognition (via speech_recognition library).
Listens for a short window after speaking, transcribes what the person said,
and passes it to the interaction engine for a response.
"""

import logging
import time

log = logging.getLogger("speech_recognition")


class SpeechRecognitionEngine:
    def __init__(self, cfg: dict):
        self.enabled         = cfg.get("enabled", True)
        self.listen_timeout  = cfg.get("listen_timeout", 5.0)   # seconds to wait for speech
        self.phrase_timeout  = cfg.get("phrase_timeout", 3.0)   # seconds of silence = end of phrase
        self.ambient_adjust  = cfg.get("ambient_adjust", 1.0)   # seconds to calibrate for pub noise
        
        self._recognizer = None
        self._microphone = None
        
        if self.enabled:
            self._init()

    def _init(self):
        try:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            self._microphone = sr.Microphone()
            
            # Adjust for ambient pub noise once on startup
            log.info("Calibrating microphone for ambient noise...")
            with self._microphone as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=self.ambient_adjust)
            
            log.info(f"Speech recognition ready (timeout={self.listen_timeout}s)")
        except ImportError:
            log.error("speech_recognition not installed. Run: pip install SpeechRecognition pyaudio")
            self.enabled = False
        except Exception as e:
            log.error(f"Microphone initialization failed: {e}")
            log.warning("Speech recognition disabled — check microphone is connected")
            self.enabled = False

    def listen(self) -> str | None:
        """
        Listen for user speech for up to listen_timeout seconds.
        Returns transcribed text, or None if nothing heard / recognition failed.
        """
        if not self.enabled:
            return None
        
        import speech_recognition as sr
        
        log.info("Listening for user response...")
        
        try:
            with self._microphone as source:
                # Listen with timeout
                audio = self._recognizer.listen(
                    source,
                    timeout=self.listen_timeout,
                    phrase_time_limit=self.phrase_timeout
                )
            
            # Transcribe using Google Speech Recognition (free, no API key needed)
            log.info("Transcribing audio...")
            text = self._recognizer.recognize_google(audio, language="en-GB")
            log.info(f"User said: {text!r}")
            return text.strip()
            
        except sr.WaitTimeoutError:
            log.info("No speech detected within timeout — user didn't respond")
            return None
        except sr.UnknownValueError:
            log.info("Speech detected but couldn't understand it (too noisy or unclear)")
            return None
        except sr.RequestError as e:
            log.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error during listening: {e}")
            return None
