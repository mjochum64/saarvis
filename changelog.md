# Changelog

## 1.1.0 (2025-04-17)
- Major Release: Push-to-Talk (PTT) is now fully integrated as a background process in the bot.
- Individual prompts (e.g., from prompt.txt/.env) are now also used for PTT audio.
- The file ptt_audio.py has been removed; all logic is now in ptt.py and started from main.py.
- Various internal improvements and refactoring.

## 1.0.2 (2025-04-17)
- Push-to-Talk (PTT) is now fully integrated into the bot and runs as a background process.
- The file ptt_audio.py has been removed; all logic is now in ptt.py and started from main.py.
- Voice recordings are still triggered via Mouse5, but are now processed directly in the bot context.

## 1.0.1 (2025-04-17)
- The bot now only responds to messages containing @Nicole. Support for /Nicole as a trigger has been removed, as Twitch treats messages starting with / as invalid commands.

## 1.0.0 (2025-04-17)
- **Release 1.0.0:** See subsequent entries for all included features and bugfixes.

## 2025-04-17
- The number of generated tokens is now configurable; the default is now 500.
- Long responses from the AI interface are now split.
- Responses are now only split at word boundaries when outputting to chat, not in the middle of words (event_message in main.py adjusted, helper function split_text_on_word_boundary added).
- Bugfix: The length of the first response block (including prefix) no longer exceeds the 500-character limit of TwitchIO. Block splitting has been adjusted accordingly.

## 2025-04-17 (Timeout & TTS Improvements)
- Timeout for ElevenLabs TTS API in main.py increased from 15s to 60s to support longer texts.
- Explicit error handling for timeouts added: users now receive a clear message if the timeout is exceeded.
- Docstring of the speak_text method expanded to Google style and notes on text length/timeout added.
- Notes on long texts and timeout behavior added to README.md and README_de.md.

## 2025-04-16
- Bot now responds to messages with '@Nicole' in chat and replies accordingly.
- New test case for Nicole detection added in test_main.py.
- Changelog file created and maintained.
