1.1 Impuls des Projekts
Im Sommersemester 2025 hat Frau Prof. XXX die Projektbegleitung des interdisziplinä-ren Master-Studienganges „Theater and Digitality“ durchgeführt. Dort hat sich schnell gezeigt, dass die Erwartungen der Studierenden und die klassischen Theorie-Inhalte weit auseinandergingen. Die Studierenden hatten wenig Interesse an tiefgehender Ma-thematik oder methodischen Trockenübungen. Sie wollten stattdessen direkt in die Pra-xis gehen und eigene Anwendungen bauen.
Oft kamen dabei sehr spezifische, künstlerische Ideen auf: Es ging zum Beispiel darum, Sprachmodelle so zu trainieren, dass sie als „Gehirn“ für Alltagsgegenstände fungieren – etwa für sprechende Uhren oder Kaffeemaschinen im Theaterkontext. Das Problem ist, dass für solche Projekte nicht nur Wissen über Fine-Tuning von LLMs (Large Language Models) fehlt, sondern vor allem die technische Basis beim Umgang mit Hardware wie dem Raspberry Pi.
1.2 Konzept
Das Projekt setzt genau an dieser Schnittstelle an. Die Idee ist, KI weg von oberflächli-cher Nutzung und selbständig Modelle rein in selbst verbaute Hardware zu bringen. Technisch bedeutet das: Wir nutzen ein vortrainiertes Modell und bauen ein eigenstän-diges System, dass es auf einem kompakten Einplatinencomputer (Raspberry Pi) läuft und über Mikrofone und Displays mit der Umwelt interagiert.
Wir kombinieren hier also Software-Engineering (Python, KI-Modelle) mit physischem  Hardware-Bau. Das fertige Projekt soll am Ende in der Lage sein, Sprache aufzuneh-men, die Emotion oder den Inhalt zu verarbeiten und direkt darauf zu reagieren – zum Beispiel durch visuelle Ausgaben auf einem Display.
1.3 Ziel der Arbeit
Hauptziel ist es, einen funktionierenden Prototyp zu bauen, der zeigt, dass so etwas mit überschaubarem Aufwand machbar ist. Dieser Prototyp soll aber kein Einzelstück blei-ben, sondern als Schablone für zukünftige Projekte dienen.



Konkret heißt das:
1.	Ein technisches Grundgerüst bauen: Ein System aus Hardware und Code, das stabil läuft.
2.	Verständlich dokumentieren: Ich möchte den gesamten Prozess so aufschrei-ben, dass auch Studierende ohne Informatik-Bachelor verstehen, wie sie eigene Hardware und KI kombinieren können, wo häufig Probleme auftreten und wie sie zu lösen sind.
3.	Transfer: Die Ergebnisse sollen nicht nur im Theater-Master genutzt werden. Der Prototyp ist auch als Anschauungsobjekt für Informatik-Studierende (z. B. im Bereich Data Science) oder als Mitmach-Station bei Veranstaltungen wie 

"""
EmotionBot - Hauptprogramm
===========================
Hier startet alles! Das Programm verbindet drei Hauptteile:
1. KI (Spracherkennung und Emotionserkennung)
2. Benutzeroberfläche (zeigt Emojis an)
3. Audio (hört über das Mikrofon zu)
"""

import threading
import os

# Reduziert die vielen Kivy-Meldungen in der Konsole
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from UI import SpeechLogApp
from AI import AIProcessor
from audio import AudioEngine


def main():
    """
    Die Hauptfunktion - hier wird der EmotionBot gestartet.
    """
    print("EmotionBot startet...")
    print("Lade KI-Modelle (das kann auf dem Raspberry Pi 30 Sekunden dauern)...")
    
    # Schritt 1: KI-Prozessor initialisieren (lädt Sprach- und Emotionsmodelle)
    ai_processor = AIProcessor()
    
    # Schritt 2: Benutzeroberfläche initialisieren (Emoji-Anzeige)
    app = SpeechLogApp()

    # Schritt 3: Definiere, was bei Audio-Ereignissen passieren soll
    def on_speech_detected():
        """Wird aufgerufen, wenn das Mikrofon jemanden sprechen hört"""
        app.show_listening()

    def on_processing_speech():
        """Wird aufgerufen, wenn die KI die aufgenommene Sprache analysiert"""
        app.show_thinking()

    def on_speech_analyzed(text, emotion):
        """Wird aufgerufen, wenn die KI fertig mit der Analyse ist"""
        print(f"Du hast gesagt: {text}")
        print(f"Erkannte Emotion: {emotion}")
        app.show_emotion(emotion)

    # Schritt 4: Audio-Engine mit unseren Callback-Funktionen erstellen
    audio_engine = AudioEngine(
        on_speech_start=on_speech_detected,
        on_processing=on_processing_speech,
        on_transcription=on_speech_analyzed
    )

    # Schritt 5: Starte das Zuhören in einem separaten Thread
    # (Dadurch läuft die Benutzeroberfläche flüssig, während wir auf Sprache hören)
    audio_thread = threading.Thread(
        target=audio_engine.start_listening,
        args=(ai_processor,),
        daemon=True  # Thread wird beendet, wenn das Hauptprogramm endet
    )
    audio_thread.start()

    # Schritt 6: Starte die grafische Benutzeroberfläche
    print("EmotionBot ist bereit! Fang an zu sprechen...")
    app.run()


if __name__ == '__main__':
    main()



"""
Benutzeroberfläche
==================
Zeigt Emoji-Animationen auf dem Bildschirm, um den Zustand und die Emotionen des Bots anzuzeigen.
Nutzt das Kivy-Framework für die grafische Oberfläche.
"""

from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from Emojis.emoji_paths import EMOJI_PATHS


class SpeechLogApp(App):
    """
    Haupt-Anwendung, die Emojis auf dem Bildschirm anzeigt.
    """
    
    def build(self):
        """
        Richtet die Benutzeroberfläche ein, wenn die App startet.
        
        Returns:
            Das Haupt-Widget (Emoji-Bild) zum Anzeigen
        """
        # Konfiguriere Fenster für Waveshare 4.3" Display (800x480 Pixel)
        Window.fullscreen = 'auto'
        Window.borderless = True
        
        # Erstelle das Bild-Widget, das Emojis zeigen wird
        self.emoji_image = Image(
            source=EMOJI_PATHS["default"][0],
            fit_mode="contain"  # Skaliere Bild passend ohne Verzerrung
        )
        
        # Animations-Status
        self.current_emotion = None
        self.emotion_index = 0
        self.animation_event = None
        
        return self.emoji_image

    @mainthread
    def show_default(self):
        """Zeige das Standard-Neutral-Emoji."""
        self.stop_animation()
        self.emoji_image.source = EMOJI_PATHS["default"][0]
        self.emoji_image.reload()

    @mainthread
    def show_listening(self):
        """Zeige das Zuhör-Emoji (wenn Mikrofon Sprache erkennt)."""
        self.stop_animation()
        self.emoji_image.source = EMOJI_PATHS["listening"][0]
        self.emoji_image.reload()

    @mainthread
    def show_thinking(self):
        """Zeige das Nachdenk-Emoji (wenn KI verarbeitet)."""
        self.stop_animation()
        self.emoji_image.source = EMOJI_PATHS["thinking"][0]
        self.emoji_image.reload()

    @mainthread
    def show_emotion(self, emotion):
        """
        Zeige und animiere ein Emotions-Emoji.
        
        Args:
            emotion: Name der Emotion ("joy", "sad", "anger", etc.)
        """
        self.stop_animation()
        self.current_emotion = emotion
        self.emotion_index = 0
        self.animate_emotion()

    def animate_emotion(self, dt=None):
        """
        Wechsle durch Emotions-Bilder, um einen Animations-Effekt zu erzeugen.
        
        Args:
            dt: Delta-Zeit (von Kivy Clock bereitgestellt, kann ignoriert werden)
        """
        if self.current_emotion and self.current_emotion in EMOJI_PATHS:
            # Hole Liste der Emoji-Bilder für diese Emotion
            emoji_images = EMOJI_PATHS[self.current_emotion]
            
            # Zeige aktuelles Bild
            self.emoji_image.source = emoji_images[self.emotion_index]
            self.emoji_image.reload()
            
            # Gehe zum nächsten Bild (springe zurück zum Anfang, wenn am Ende)
            self.emotion_index = (self.emotion_index + 1) % len(emoji_images)
            
            # Plane nächstes Frame in 0.5 Sekunden
            self.animation_event = Clock.schedule_once(self.animate_emotion, 0.5)

    def stop_animation(self):
        """Stoppe jede aktuell laufende Emoji-Animation."""
        if self.animation_event:
            self.animation_event.cancel()
            self.animation_event = None
        self.current_emotion = None


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


"""
Audio-Engine
============
Hört dem Mikrofon zu und erkennt, wann jemand spricht.
Nutzt Voice Activity Detection (VAD), um zu wissen, wann Sprache beginnt und endet.
"""

import pyaudio
import webrtcvad
import time
from collections import deque
from config import (
    FORMAT, CHANNELS, RATE, CHUNK_SIZE, 
    VAD_AGGRESSIVENESS, SILENCE_DURATION_MS
)


class AudioEngine:
    """
    Verwaltet Mikrofon-Eingabe und Spracherkennung.
    """
    
    def __init__(self, on_speech_start=None, on_processing=None, on_transcription=None):
        """
        Initialisiert die Audio-Engine mit Callback-Funktionen.
        
        Args:
            on_speech_start: Funktion, die aufgerufen wird, wenn Sprache erkannt wird
            on_processing: Funktion, die aufgerufen wird, wenn Verarbeitung beginnt
            on_transcription: Funktion, die mit Ergebnissen aufgerufen wird (text, emotion)
        """
        # Voice Activity Detector - erkennt, ob Audio Sprache enthält
        self.vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
        
        # Speichere Callback-Funktionen
        self.on_speech_start = on_speech_start
        self.on_processing = on_processing
        self.on_transcription = on_transcription
        
        # Kontroll-Flag für die Zuhör-Schleife
        self.is_running = True
        
        # Tatsächliche Sample-Rate (kann von der Konfiguration abweichen, falls Hardware es nicht unterstützt)
        self.actual_rate = RATE

    def _find_working_audio_config(self, audio_interface):
        """
        Probiert verschiedene Sample-Raten aus, um eine zu finden, die mit deinem Mikrofon funktioniert.
        
        Args:
            audio_interface: PyAudio-Instanz
            
        Returns:
            tuple: (sample_rate, chunk_size) die funktioniert
        """
        # WebRTC VAD unterstützt nur diese spezifischen Sample-Raten
        supported_rates = [16000, 48000, 32000, 8000]
        
        for rate in supported_rates:
            try:
                # Versuche, einen Audio-Stream mit dieser Rate zu öffnen
                test_stream = audio_interface.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=rate,
                    input=True,
                    frames_per_buffer=int(rate * 30 / 1000)  # 30ms Chunks
                )
                test_stream.close()
                
                print(f"✓ Nutze Sample-Rate: {rate} Hz")
                return rate, int(rate * 30 / 1000)
                
            except Exception as e:
                print(f"✗ Sample-Rate {rate} Hz wird nicht unterstützt: {e}")
                continue
        
        # Wenn wir hier ankommen, hat keine Sample-Rate funktioniert
        raise RuntimeError(
            "Keine unterstützte Audio-Konfiguration gefunden. "
            "Bitte überprüfe deine Mikrofon-Verbindung."
        )

    def start_listening(self, ai_processor):
        """
        Haupt-Zuhör-Schleife - überwacht kontinuierlich das Mikrofon auf Sprache.
        
        Args:
            ai_processor: AIProcessor-Instanz zum Analysieren der aufgenommenen Sprache
        """
        # Initialisiere PyAudio
        audio_interface = pyaudio.PyAudio()
        
        # Zeige verfügbare Mikrofone zum Debuggen
        print("\nVerfügbare Mikrofone:")
        for i in range(audio_interface.get_device_count()):
            device_info = audio_interface.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"  Gerät {i}: {device_info['name']}")
        
        # Finde eine Sample-Rate, die mit dem Mikrofon funktioniert
        try:
            self.actual_rate, chunk_size = self._find_working_audio_config(audio_interface)
        except RuntimeError as e:
            print(f"Fehler: {e}")
            audio_interface.terminate()
            return
        
        # Öffne den Mikrofon-Stream
        try:
            stream = audio_interface.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=self.actual_rate,
                input=True,
                frames_per_buffer=chunk_size
            )
        except Exception as e:
            print(f"Mikrofon konnte nicht geöffnet werden: {e}")
            audio_interface.terminate()
            return

        # Speicher für aufgenommene Audio-Chunks
        aufgenommene_frames = deque()
        
        # Status-Tracking
        nimmt_auf = False
        stille_start_zeit = None

        try:
            # Haupt-Zuhör-Schleife
            while self.is_running:
                try:
                    # Lese ein Audio-Chunk vom Mikrofon
                    audio_chunk = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                except OSError:
                    # Ignoriere Buffer-Overflow-Fehler
                    continue

                # Prüfe, ob dieser Chunk Sprache enthält
                enthaelt_sprache = self.vad.is_speech(audio_chunk, self.actual_rate)
                
                if enthaelt_sprache:
                    # Sprache erkannt!
                    if not nimmt_auf:
                        # Das ist der Beginn neuer Sprache
                        if self.on_speech_start:
                            self.on_speech_start()
                        nimmt_auf = True
                    
                    # Speichere diesen Audio-Chunk
                    aufgenommene_frames.append(audio_chunk)
                    stille_start_zeit = None
                    
                elif nimmt_auf:
                    # Keine Sprache in diesem Chunk, aber wir nehmen noch auf
                    aufgenommene_frames.append(audio_chunk)
                    
                    # Verfolge, wie lange die Stille schon andauert
                    if stille_start_zeit is None:
                        stille_start_zeit = time.time()
                    else:
                        stille_dauer = (time.time() - stille_start_zeit) * 1000
                        
                        # Wenn die Stille lange genug war, stoppe die Aufnahme
                        if stille_dauer > SILENCE_DURATION_MS:
                            # Benachrichtige, dass wir verarbeiten
                            if self.on_processing:
                                self.on_processing()
                            
                            # Sende Audio zur KI für Transkription und Emotionserkennung
                            results = ai_processor.transcribe(
                                list(aufgenommene_frames), 
                                self.actual_rate
                            )
                            
                            # Sende Ergebnisse über Callback zurück
                            if self.on_transcription:
                                for result in results:
                                    self.on_transcription(
                                        result['text'], 
                                        result['emotion']
                                    )
                            
                            # Zurücksetzen für nächste Aufnahme
                            aufgenommene_frames.clear()
                            nimmt_auf = False
                            stille_start_zeit = None
                            
        finally:
            # Räume Audio-Ressourcen auf
            stream.stop_stream()
            stream.close()
            audio_interface.terminate()


"""
Konfigurationsdatei
===================
Hier sind alle Einstellungen für den EmotionBot gespeichert.
Du kannst diese Werte ändern, um das Verhalten anzupassen.
"""

import pyaudio
import os

# AUDIO-EINSTELLUNGEN


# Audio-Format: 16-bit bedeutet, dass jedes Audio-Sample 16 Bits Daten nutzt
FORMAT = pyaudio.paInt16

# Kanäle: 1 = Mono (ein Mikrofon), 2 = Stereo (links und rechts)
CHANNELS = 1

# Sample-Rate: Wie viele Audio-Samples pro Sekunde (48.000 ist hohe Qualität)
RATE = 48000

# Chunk-Dauer: Audio wird in 30-Millisekunden-Stücken verarbeitet
# (Das braucht die Spracherkennungs-Bibliothek so)
CHUNK_DURATION_MS = 30
CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)

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
WHISPER_MODEL_SIZE = "small"

# Pfad zum Emotionserkennungs-Modell
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMOTION_MODEL_NAME = os.path.join(BASE_DIR, "models", "emotion_classifier")








