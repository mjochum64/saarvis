# saarvis – Twitch Chatbot with OpenAI and ElevenLabs TTS

**Current version:** 1.4.0

## Description

saarvis is a modern Twitch chatbot written in Python that leverages OpenAI for AI-powered responses and ElevenLabs for text-to-speech (TTS).
Configuration is managed via a `.env` file.

## Features

- Welcomes new users in the Twitch chat
- AI-powered responses to messages containing @Nicole
- Text-to-speech of responses via ElevenLabs (TTS)
- Flexible configuration of voice and model via environment variables
- Reliable audio playback using mpg123/mpv
- Easy adjustment of the OpenAI model and API keys via `.env`
- Status check of the OpenAI interface at startup

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
   IGNORED_USERS=saaromansbot,streamelements,anotherbot
   ```

3. **Create prompt.txt**:

   ```bash
   cp prompt.txt.example prompt.txt   
   ```

   The content of the provided prompt is just an example and should be adapted to your own needs.

## Dependency Check

On startup, saarvis checks for all required environment variables. If any are missing, the bot will exit with a clear error message. Make sure your `.env` file contains at least the following:

```env
TMI_TOKEN=<your_twitch_token>
TWITCH_CHANNEL=<your_channel>
OPENAI_API_KEY=<your_openai_key>
ELEVENLABS_API_KEY=<your_elevenlabs_key>
ELEVENLABS_VOICE_ID=<your_voice_id>
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
IGNORED_USERS=saaromansbot,streamelements,anotherbot
```

## Customizing the Prompt

You can customize the bot's personality and behavior by editing `prompt.txt`. For example:

```prompt
You are a helpful, friendly chatbot for Twitch.
Please always reply in the language you are addressed in.
Your answers should be short and concise.
If you are not sure what to answer, simply say "I'm not sure, but I'll do my best to help!".
The answers should always use informal "you".
```

## Ignoring Specific Users

You can configure which users should be ignored by the bot (e.g., other bots like "saaromansbot" or "streamelements") using the IGNORED_USERS environment variable in your `.env` file:

```
IGNORED_USERS=saaromansbot,streamelements,anotherbot
```

This list is case-insensitive and comma-separated. If not set, the default is `saaromansbot, streamelements`.

Messages from these users will be ignored by the bot and not processed.

## Push-to-Talk (PTT)

saarvis supports Push-to-Talk (PTT) for voice input. By default, recording is triggered by Mouse5 (button9). The audio is transcribed using OpenAI Whisper, sent to the AI for a response, and the answer is played back using ElevenLabs TTS.

- To use PTT, simply press Mouse5 while the bot is running.
- Make sure your microphone is set up and accessible.
- All required dependencies for PTT are installed automatically on first run.

## Usage

Start the bot with:

```bash
uv run main.py
```

![Screenshot: Bot Startup](start.png)

All required modules will be installed on first start.
