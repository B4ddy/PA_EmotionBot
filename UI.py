"""
Benutzeroberfläche
==================
Zeigt Emoji-Animationen auf dem Bildschirm, um den Zustand und die Emotionen des Bots anzuzeigen.
Nutzt das Kivy-Framework für die grafische Oberfläche.
"""

from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.clock import mainthread, Clock
from Emojis.emoji_paths import EMOJI_PATHS


class KivyUserInterface(App):
    """
    Haupt-Anwendung, die Emojis auf dem Bildschirm anzeigt.
    """
    
    def build(self):
        """
        Richtet die Benutzeroberfläche ein, wenn die App startet.
        
        Returns:
            Das Haupt-Layout zum Anzeigen von Emoji und Schließen-Button
        """
        root = FloatLayout()
        
        # Erstelle das Bild-Widget, das Emojis zeigen wird
        self.emoji_image = Image(
            source=EMOJI_PATHS["default"][0],
            fit_mode="contain"  # Skaliere Bild passend ohne Verzerrung
        )
        root.add_widget(self.emoji_image)

        close_button = Button(
            text="X",
            size_hint=(None, None),
            size=(48, 48),
            pos_hint={"right": 0.99, "top": 0.99}
        )
        close_button.bind(on_release=self.close_application)
        root.add_widget(close_button)
        
        # Animations-Status
        self.current_emotion = None
        self.emotion_index = 0
        self.animation_event = None
        
        return root
    
    @mainthread
    def show_state(self, state):
        """Zeige ein einzelnes (nicht-animiertes) Emoji für einen Bot-Zustand.
        
        Args:
            state: Schlüssel aus EMOJI_PATHS, z.B. "default", "listening", "thinking"
        """
        self.stop_animation()
        self.emoji_image.source = EMOJI_PATHS[state][0]
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

    def close_application(self, _instance):
        """Beendet die Anwendung über den X-Button."""
        self.stop()
