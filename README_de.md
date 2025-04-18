# saarvis – Twitch-Chatbot mit OpenAI und ElevenLabs TTS

**Aktuelle Version:** 1.1.0

## Projektbeschreibung

saarvis ist ein moderner Twitch-Chatbot, geschrieben in Python, der OpenAI für KI-gestützte Antworten und ElevenLabs für Text-to-Speech (TTS) nutzt. Die Konfiguration erfolgt über eine `.env`-Datei.

## Funktionen

- Begrüßt neue Nutzer im Twitch-Chat
- KI-gestützte Antworten auf Nachrichten mit @Nicole
- Text-to-Speech der Antworten über ElevenLabs (TTS)
- Flexible Konfiguration von Stimme und Modell über Umgebungsvariablen
- Zuverlässige Audiowiedergabe mit mpg123/mpv
- Einfache Anpassung des OpenAI-Modells und der API-Keys über `.env`
- Statusprüfung der OpenAI-Schnittstelle beim Start

## Hinweis zur Bot-Ansprache

Seit Version 1.0.1: Der Bot reagiert nur auf Nachrichten, die @Nicole enthalten. Die Verwendung von /Nicole als Trigger ist nicht mehr möglich, da Twitch Nachrichten mit / als ungültige Befehle behandelt.

## Push-to-Talk (PTT) Integration

Seit Version 1.0.2 ist die Push-to-Talk-Funktionalität direkt in den Bot integriert und läuft als Hintergrundprozess. Die Aufnahme wird wie gewohnt über Maus5 ausgelöst, die Verarbeitung (Transkription, KI-Antwort, TTS) erfolgt direkt im Bot-Prozess. Die Datei `ptt_audio.py` wird nicht mehr benötigt.

## Entfernung von ptt_audio.py

Die Datei `ptt_audio.py` wurde entfernt, da die gesamte Funktionalität jetzt in `ptt.py` und `main.py` enthalten ist.

## Installation

Für die Installation wird das Tool [uv](https://docs.astral.sh/uv/) anstelle des üblichen pip verwendet. Dies vereinfacht und beschleunigt die Installation erheblich.

1. **Repository klonen**

   ```bash
   git clone https://github.com/mjochum64/saarvis
   cd saarvis
   ```

2. **.env-Datei erstellen** (Beispiel):

   ```env
   TMI_TOKEN=<dein_twitch_token>
   TWITCH_CHANNEL=<dein_channel>
   OPENAI_API_KEY=<dein_openai_key>
   OPENAI_MODEL=gpt-3.5-turbo
   ELEVENLABS_API_KEY=<dein_elevenlabs_key>
   ELEVENLABS_VOICE_ID=<deine_voice_id>
   ELEVENLABS_MODEL_ID=eleven_multilingual_v2
   ```

3. **prompt.txt erstellen**:

   ```bash
   cp prompt.txt.example prompt.txt   
   ```

   Der bereitgestellte Prompt ist nur ein Beispiel und sollte an die eigenen Bedürfnisse angepasst werden.

## Nutzung

Starte den Bot mit:

```bash
uv run main.py
```

![Screenshot: Bot-Start](start.png)

Alle benötigten Module werden beim ersten Start automatisch installiert.

## Systemanforderungen

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- mpg123 oder mpv für Audiowiedergabe
- [ElevenLabs](https://elevenlabs.io/) Konto für TTS

## Hinweis zu langen Texten und Timeout bei TTS

**Achtung:** Die Sprachausgabe (Text-to-Speech, TTS) über ElevenLabs kann bei sehr langen Texten (>1000 Zeichen) zu Zeitüberschreitungen führen. Das Timeout für die API-Anfrage beträgt 60 Sekunden. Sollte ein Timeout auftreten, kürze den Text oder versuche es später erneut.

## Tests

Tests befinden sich im Verzeichnis `tests/` und können mit folgendem Befehl ausgeführt werden:

```bash
uv run pytest tests/test_main.py
```

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe [LICENSE](LICENSE) für Details.

## Autor

Martin Jochum <mjochum64@gmail.com>

---
*Erstellt am 16.04.2025*
