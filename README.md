# saarvis – Twitch Chatbot with OpenAI and ElevenLabs TTS

**Current version:** 1.1.0

## Project Description

saarvis is a modern Twitch chatbot written in Python that leverages OpenAI for AI-powered responses and ElevenLabs for text-to-speech (TTS). Configuration is managed via a `.env` file.

## Features

- Welcomes new users in the Twitch chat
- AI-powered responses to messages containing @Nicole
- Text-to-speech of responses via ElevenLabs (TTS)
- Flexible configuration of voice and model via environment variables
- Reliable audio playback using mpg123/mpv
- Easy adjustment of the OpenAI model and API keys via `.env`
- Status check of the OpenAI interface at startup

## Bot Trigger Notice

Since version 1.0.1: The bot only responds to messages containing @Nicole. Using /Nicole as a trigger is no longer possible, as Twitch treats messages starting with / as invalid commands.

## Push-to-Talk (PTT) Integration

Since version 1.0.2, push-to-talk functionality is directly integrated into the bot and runs as a background process. Recording is triggered as usual via Mouse5, and processing (transcription, AI response, TTS) happens directly within the bot process. The file `ptt_audio.py` is no longer required.

## Removal of ptt_audio.py

The file `ptt_audio.py` has been removed, as all its functionality is now included in `ptt.py` and `main.py`.

## Installation

For installation, the [uv](https://docs.astral.sh/uv/) tool is used instead of the more common pip. This makes installation easier and much faster.

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

![Screenshot: Bot Startup](start.png)

All required modules will be installed on first start.
