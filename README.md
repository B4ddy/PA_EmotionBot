# EmotionBot

Ein Raspberry-Pi-basiertes System zur Echtzeit-Emotionserkennung aus gesprochener Sprache, entwickelt im Rahmen einer Bachelorarbeit. Der EmotionBot hört kontinuierlich auf Spracheingaben, transkribiert sie mithilfe eines vortrainierten Sprachmodells und klassifiziert die erkannte Emotion, die anschließend über animierte Emojis auf einem Display visualisiert wird.

---

## Funktionsweise

Der Bot durchläuft bei jeder Spracheingabe vier Schritte:

1. **Aufnahme** – Ein USB-Mikrofon nimmt kontinuierlich Audio auf. Mithilfe von Voice Activity Detection (VAD) wird erkannt, wann jemand spricht.
2. **Transkription** – Das aufgenommene Audio wird mit [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (einer optimierten Implementierung von OpenAIs Whisper-Modell) in Text umgewandelt.
3. **Emotionsklassifikation** – Der transkribierte Text wird an ein feinabgestimmtes DistilBERT-Modell übergeben, das eine der sechs Emotionen vorhersagt: `joy`, `sad`, `anger`, `fear`, `love`, `surprise`.
4. **Visualisierung** – Die erkannte Emotion wird über eine Kivy-basierte GUI als animiertes Emoji auf dem angeschlossenen Display angezeigt.

---

## Voraussetzungen

### Hardware

- **Raspberry Pi 5** (empfohlen, getestet mit 8 GB RAM)
- **USB-Mikrofon**
- **Display** (getestet mit Waveshare 4.3" DSI LCD, 800×480)

### Software

- Python 3.10+
- pip

---

## Installation

### 1. Repository klonen

```bash
git clone <github url später>
cd EmotionBot
```

### 2. Emotionserkennungs-Modell herunterladen

Das Modell wird lokal unter `google drive link oder so` erwartet. Alle Modelldateien können von Hugging Face heruntergeladen werden:

```bash
mkdir -p models/emotion_classifier
cd models/emotion_classifier
```

Dann alle Dateien von folgender Seite herunterladen:  
👉 https://huggingface.co/tsid7710/distillbert-emotion-model/tree/main

Anschließend zurück ins Projektverzeichnis:

```bash
cd ../..
```

### 3. Systemabhängigkeiten installieren

```bash
sudo apt update
sudo apt install -y python3-pip portaudio19-dev python3-pyaudio
```

### 4. PyTorch installieren (CPU-optimiert für Raspberry Pi)

```bash
pip3 install torch --index-url https://download.pytorch.org/whl/cpu
```

### 5. Python-Pakete installieren

```bash
pip3 install -r requirements.txt
```

---

## Starten

```bash
python3 main.py
```

Beim ersten Start werden die KI-Modelle in den Arbeitsspeicher geladen – das dauert auf dem Raspberry Pi erfahrungsgemäß 20–30 Sekunden. Danach ist der Bot bereit und wartet auf Spracheingaben.

---

## Projektstruktur

```
EmotionBot/
├── main.py          # Einstiegspunkt, verbindet alle Komponenten
├── AI.py            # Transkription (Whisper) und Emotionsklassifikation (DistilBERT)
├── audio.py         # Mikrofonaufnahme und Voice Activity Detection
├── UI.py            # Kivy-GUI, Emoji-Anzeige und Zustandsanimationen
├── config.py        # Zentrale Konfigurationsdatei
├── requirements.txt # Python-Abhängigkeiten
├── Emojis/          # Emoji-Bilder für jede Emotion (PNG)
├── models/          # Lokale Modellgewichte (nicht im Repository enthalten)
└── trainingcode/    # Skripte zum Feinabstimmen des Emotionsklassifikators
```

---

## Konfiguration

Alle relevanten Parameter befinden sich in [`config.py`](config.py):

### Whisper-Modellgröße (`WHISPER_MODEL_SIZE`)

| Wert | Geschwindigkeit | Genauigkeit | RAM-Bedarf |
|------|----------------|-------------|------------|
| `"tiny"` | sehr schnell | gering | ~75 MB |
| `"base"` | schnell | moderat | ~150 MB |
| `"small"` | moderat | gut | ~500 MB |
| `"medium"` | langsam | sehr gut | ~1,5 GB |

Für den Raspberry Pi 5 hat sich `"base"` als guter Kompromiss erwiesen.

### VAD-Aggressivität (`VAD_AGGRESSIVENESS`)

Steuert, wie empfindlich die Sprachaktivitätserkennung auf Hintergrundgeräusche reagiert:

- `0` – wenig aggressiv, nimmt auch leise Sprache auf
- `3` – sehr aggressiv, filtert Hintergrundgeräusche zuverlässig heraus

### Stille-Schwellenwert (`SILENCE_DURATION_MS`)

Gibt an, wie lange (in Millisekunden) nach dem letzten Sprachsignal gewartet wird, bevor die Aufnahme beendet wird. Standardwert: `1000` ms.

---

## Verwendete Bibliotheken

| Bibliothek | Zweck | Link |
|---|---|---|
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Spracherkennung (ASR) | https://github.com/SYSTRAN/faster-whisper |
| [transformers](https://github.com/huggingface/transformers) | Emotionsklassifikation (DistilBERT) | https://huggingface.co/docs/transformers |
| [PyTorch](https://pytorch.org/) | Deep-Learning-Backend | https://pytorch.org/ |
| [webrtcvad](https://github.com/wiseman/py-webrtcvad) | Voice Activity Detection | https://github.com/wiseman/py-webrtcvad |
| [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) | Mikrofonzugriff | https://people.csail.mit.edu/hubert/pyaudio/ |
| [Kivy](https://kivy.org/) | GUI-Framework | https://kivy.org/ |
| [NumPy](https://numpy.org/) | Audiodatenverarbeitung | https://numpy.org/ |

---

## Bekannte Einschränkungen

- Das Whisper-Modell erwartet englischsprachige Eingaben (`language="en"`) Das Emotionsmodell ist auch nur auf einem englischen Datensatz trainiert. könnte übersetzt werden. Für andere Sprachen muss der Parameter in [`AI.py`](AI.py) angepasst werden.
- Die Emotionsklassifikation arbeitet auf Textebene – prosodische Merkmale (Tonhöhe, Sprechgeschwindigkeit) werden nicht berücksichtigt.
- Auf dem Raspberry Pi kann es bei längeren Äußerungen zu spürbaren Verarbeitungsverzögerungen kommen, da alle Berechnungen auf der CPU stattfinden.

---

## Fehlerbehebung

**„Keine unterstützte Audio-Konfiguration gefunden"**  
→ Mikrofon prüfen, ggf. anderen USB-Port verwenden. Mit `arecord -l` lassen sich verfügbare Aufnahmegeräte auflisten.

**Modelle laden sehr langsam**  
→ Das ist auf dem Raspberry Pi normal. Ein kleineres Whisper-Modell (`"tiny"` oder `"base"`) kann die Ladezeit deutlich reduzieren.

**Emotionserkennung liefert unplausible Ergebnisse**  
→ Das Modell wurde auf englischsprachigen Texten trainiert und funktioniert am besten mit klaren, ausdrucksstarken Formulierungen. Kurze oder mehrdeutige Äußerungen können zu Fehlklassifikationen führen.


**Ist zu sensibel oder nicht sensibel genug**  
→ Bei Pi OS kann rechts oben auf das Mikrofon geklickt werden und die sensitivität angepasst werden. wenn kein Mikro angezeigt wird, wird es nicht erkannt.