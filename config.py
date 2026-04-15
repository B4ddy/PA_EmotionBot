"""
Konfigurationsdatei
===================
Hier sind alle Einstellungen für den EmotionBot gespeichert.
Du kannst diese Werte ändern, um das Verhalten anzupassen.
"""

import os

# AUDIO-EINSTELLUNGEN

# Audio-Format: 16-bit PCM (pyaudio.paInt16 = 8)
FORMAT = 8

# Kanäle: 1 = Mono (ein Mikrofon), 2 = Stereo (links und rechts)
CHANNELS = 1

# Sample-Rate: Wie viele Audio-Samples pro Sekunde (48.000 ist hohe Qualität)
RATE = 48000

# Chunk-Dauer: Audio wird in 30-Millisekunden-Stücken verarbeitet
# (Das braucht die Spracherkennungs-Bibliothek so)
CHUNK_DURATION_MS = 30

# Voice Activity Detection (VAD) Aggressivität
# Skala: 0 (am wenigsten aggressiv) bis 3 (am aggressivsten)
# Höher = filtert Hintergrundgeräusche besser, könnte aber leise Sprache überhören
VAD_AGGRESSIVENESS = 3

# Wie lange soll in Stille gewartet werden, bevor die Aufnahme stoppt? (in Millisekunden)
# 1000 ms = 1 Sekunde
SILENCE_DURATION_MS = 1000



# KI-MODELL-EINSTELLUNGEN

# Whisper-Modellgrößen: "tiny", "base", "small", "medium", "large"
# Größer = genauer, aber langsamer und braucht mehr Speicher
# Empfehlung für Raspberry Pi 5: "small" (gute Balance)
WHISPER_MODEL_SIZE = "tiny"

# Pfad zum Emotionserkennungs-Modell
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMOTION_MODEL_NAME = os.path.join(BASE_DIR, "models", "test")
