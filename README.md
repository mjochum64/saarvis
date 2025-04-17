# saarvis – Twitch Chatbot with OpenAI and ElevenLabs TTS

## Project Description

saarvis is a modern Twitch chatbot based on Python that uses OpenAI for AI-powered responses and ElevenLabs for text-to-speech. Configuration is done via a .env file.

## Features

- Welcomes new users in the Twitch chat
- AI-powered responses to messages with @Nicole
- Text-to-speech of responses via ElevenLabs (TTS)
- Flexible configuration of voice and model via environment variables
- Reliable audio playback via mpg123/mpv
- Easy adjustment of the OpenAI model and API keys via .env
- Status check of the OpenAI interface at startup

## Installation

For installation, I use the tool [uv](https://docs.astral.sh/uv/) instead of the more commonly expected pip. This makes installation easier and much faster.

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

   The content of the provided prompt is just an example and should be adapted to your own needs.

## Usage

Start the bot with:

```bash
uv run main.py
```

![alt text](start.png)

All required modules will be installed on first start.

## System Requirements

- Python 3.13 
- [uv](https://docs.astral.sh/uv/) 
- mpg123 or mpv for audio playback
- [ElevenLabs](https://elevenlabs.io/) account for TTS

## Tests

Tests are located in the `tests/` directory and can be started as follows:

```bash
uv run pytest tests/test_main.py
```

![alt text](tests.png)


## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author
Martin Jochum <mjochum64@gmail.com>

---
*Created on 16.04.2025*
