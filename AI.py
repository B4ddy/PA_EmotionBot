"""
KI-Prozessor
============
Kümmert sich um zwei KI-Aufgaben:
1. Sprache-zu-Text: Wandelt gesprochene Worte in geschriebenen Text um (mit Whisper)
2. Emotionserkennung: Analysiert den Text, um die Emotion des Sprechers zu erkennen
"""

import torch
import numpy as np
from faster_whisper import WhisperModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from config import WHISPER_MODEL_SIZE, EMOTION_MODEL_NAME


class AIProcessor:
    """
    Verarbeitet Audio, um Text zu extrahieren und Emotionen zu erkennen.
    """
    
    def __init__(self):
        """
        Lädt die KI-Modelle beim Start.
        Das dauert eine Weile, passiert aber nur einmal beim Programmstart.
        """
        print("Lade Whisper Spracherkennungs-Modell...")
        # Nutze CPU-Modus mit int8, um Speicher auf dem Raspberry Pi zu sparen
        self.whisper = WhisperModel(
            WHISPER_MODEL_SIZE, 
            device="cpu", 
            compute_type="int8"
        )
        
        print("Lade Emotionserkennungs-Modell...")
        self.tokenizer = AutoTokenizer.from_pretrained(EMOTION_MODEL_NAME)
        self.emotion_model = AutoModelForSequenceClassification.from_pretrained(
            EMOTION_MODEL_NAME
        )
        
        # Liste der Emotionen, die das Modell erkennen kann
        self.emotions = ["sad", "joy", "love", "anger", "fear", "surprise"]
        
        print("KI-Modelle erfolgreich geladen!")

    def detect_emotion(self, text):
        """
        Analysiert einen Text, um herauszufinden, welche Emotion er ausdrückt.
        
        Args:
            text: Der zu analysierende Text (String)
            
        Returns:
            emotion: Eine von ["sad", "joy", "love", "anger", "fear", "surprise"]
        """
        # Wandle den Text in Zahlen um, die das Modell versteht
        inputs = self.tokenizer(text, return_tensors="pt")
        
        # Führe das Emotionserkennungs-Modell aus (ohne Gradienten zu berechnen)
        with torch.inference_mode():
            logits = self.emotion_model(**inputs).logits
        
        # Finde heraus, welche Emotion den höchsten Score hat
        prediction_index = torch.argmax(logits, dim=-1).item()
        erkannte_emotion = self.emotions[prediction_index]
        
        return erkannte_emotion

    def transcribe(self, audio_frames, sample_rate=16000):
        """
        Wandelt aufgenommenes Audio in Text um und erkennt Emotionen.
        
        Args:
            audio_frames: Liste von Audio-Daten-Chunks (Bytes)
            sample_rate: Wie viele Samples pro Sekunde im Audio
            
        Returns:
            results: Liste von Dictionaries mit 'text' und 'emotion' Schlüsseln
        """
        # Kombiniere alle Audio-Chunks zu einem Stück
        audio_data = b"".join(audio_frames)
        
        # Wandle Bytes in Zahlen zwischen -1.0 und 1.0 um
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Whisper erwartet 16kHz Audio, also resample falls nötig
        if sample_rate != 16000:
            duration = len(audio_array) / sample_rate
            target_length = int(duration * 16000)
            audio_array = np.interp(
                np.linspace(0, len(audio_array), target_length),
                np.arange(len(audio_array)),
                audio_array
            )
        
        # Nutze Whisper, um Sprache in Text umzuwandeln
        # beam_size=1 bedeutet schnellere Verarbeitung (gut für Raspberry Pi)
        segments, _ = self.whisper.transcribe(
            audio_array, 
            language="en", 
            beam_size=1
        )
        
        # Verarbeite jedes Sprach-Segment
        results = []
        for segment in segments:
            emotion = self.detect_emotion(segment.text)
            results.append({
                "text": segment.text, 
                "emotion": emotion
            })
        
        return results
