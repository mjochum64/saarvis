# saarvis – Twitch Chatbot with OpenAI and ElevenLabs TTS

## Project Description

saarvis is a modern Twitch chatbot based on Python, utilizing OpenAI for AI responses and ElevenLabs for text-to-speech. Configuration is managed via a .env file.

## Features

- Welcomes new users in the Twitch chat
- AI-powered responses to messages with @Nicole
- Text-to-speech output of responses via ElevenLabs (TTS)
- Flexible configuration of voice and model via environment variables
- Reliable audio playback using mpg123/mpv
- Easy adjustment of OpenAI model and API keys via .env
- Status check of the OpenAI API on startup

## Installation

For installation, the [uv](https://docs.astral.sh/uv/) tool is used instead of pip, making the process simpler and much faster.

1. **Clone the repository**

   ```bash
   git clone https://github.com/mjochum64/saarvis
   cd saarvis
   ```

2. **Create a .env file** (example):

   ```env
   TMI_TOKEN=<your_twitch_token>
   TWITCH_CHANNEL=<your_channel>
   OPENAI_API_KEY=<your_openai_key>
   OPENAI_MODEL=gpt-3.5-turbo
   ELEVENLABS_API_KEY=<your_elevenlabs_key>
   ELEVENLABS_VOICE_ID=<your_voice_id>
   ELEVENLABS_MODEL_ID=eleven_multilingual_v2
   ```

3. **Create prompt.txt**:

   ```bash
   cp prompt.txt.example prompt.txt   
   ```

   The provided prompt is just an example and should be adapted to your needs.

## Usage

Start the bot with:

```bash
uv run main.py
```

On the first run, all required modules will be installed automatically.

## System Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- mpg123 or mpv for audio playback
- [ElevenLabs](https://elevenlabs.io/) account for TTS

## Hinweis zu langen Texten und Timeout bei TTS

**Achtung:** Die Sprachausgabe (Text-to-Speech, TTS) über ElevenLabs kann bei sehr langen Texten (>1000 Zeichen) zu Zeitüberschreitungen führen. Das Timeout für die API-Anfrage beträgt 60 Sekunden. Sollte ein Timeout auftreten, kürze den Text oder versuche es später erneut.

## Tests

Tests are located in the `tests/` directory and can be run with:

```bash
uv run pytest tests/test_main.py
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

Martin Jochum <mjochum64@gmail.com>

---
*Created on 16.04.2025*
