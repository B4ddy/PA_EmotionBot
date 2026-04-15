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
from UI import KivyUserInterface
from AI import AIProcessor
from audio import AudioEngine

# Reduziert die vielen Kivy-Meldungen in der Konsole
os.environ['KIVY_NO_CONSOLELOG'] = '1'

def main():
    """
    Die Hauptfunktion - hier wird der EmotionBot gestartet.
    """
    print("EmotionBot startet...")
    print("Lade KI-Modelle (das kann auf dem Raspberry Pi 30 Sekunden dauern)...")
    
    # Schritt 1: KI-Prozessor initialisieren (lädt Sprach- und Emotionsmodelle)
    ai_processor = AIProcessor()
    
    # Schritt 2: Benutzeroberfläche initialisieren (Emoji-Anzeige)
    app = KivyUserInterface()

    # Schritt 3: Definiere, was bei Audio-Ereignissen passieren soll
    def on_speech_detected():
        """Wird aufgerufen, wenn das Mikrofon jemanden sprechen hört"""
        app.show_state("listening")

    def on_processing_speech():
        """Wird aufgerufen, wenn die KI die aufgenommene Sprache analysiert"""
        app.show_state("thinking")

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
