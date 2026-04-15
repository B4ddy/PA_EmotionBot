"""
Audio-Engine
============
Hört dem Mikrofon zu und erkennt, wann jemand spricht.
Nutzt Voice Activity Detection (VAD), um zu wissen, wann Sprache beginnt und endet.
"""

import pyaudio
import webrtcvad
import time
from config import (
    FORMAT, CHANNELS, RATE,
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
                
                print(f" Nutze Sample-Rate: {rate} Hz")
                return rate, int(rate * 30 / 1000)
                
            except Exception as e:
                print(f" Sample-Rate {rate} Hz wird nicht unterstützt: {e}")
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
        aufgenommene_frames = []
        
        # Status-Tracking
        nimmt_auf = False
        stille_start_zeit = None

        try:
            # Haupt-Zuhör-Schleife
            while self.is_running:
                try:
                    # Lese ein Audio-Chunk vom Mikrofon
                    audio_chunk = stream.read(chunk_size, exception_on_overflow=False)
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
