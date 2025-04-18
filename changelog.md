# Changelog

## 1.4.0 (2025-04-18)
- Version bump to 1.4.0 in all relevant files.
- Improved error handling and logging in PTT and main bot logic.
- PTT: Now outputs OpenAI responses to Twitch chat and uses the same message splitting logic as normal chat responses (max 500 characters, word boundary).
- PTT integration refactored: PTTRecorder now accepts a callback for chat output, ensuring thread-safe and async message delivery.
- Codebase: Consistent type hints, improved docstrings, and adherence to PEP 8/PEP 257.
- Dependency check and cleanup of temporary audio files at startup improved.
- README updated for new features and configuration options.
- Security and code quality review performed; recommendations implemented.

## 1.3.0 (2025-04-18)
- Push-to-Talk (PTT) now also outputs the OpenAI response in the Twitch chat, not just as audio.
- PTT chat output uses the same message splitting logic as normal chat responses (max 500 characters, word boundary).
- Refactored PTT integration: PTTRecorder now accepts a callback for chat output, ensuring thread-safe and async message delivery.
- Improved logging: switched to lazy % formatting and more precise exception handling throughout the codebase.
- Bumped version to 1.3.0 in all relevant files.

## 1.2.0 (2025-04-18)
- Consistently added type hints in ptt.py.
- Replaced print statements with logging in ptt.py, unified logging levels and docstrings.
- Improved error handling in ptt.py and added logging for error cases.
- Added dependency check for critical environment variables in main.py.
- Integrated cleanup mechanism for temporary audio files (mp3, aufnahme.wav) at startup in main.py.
- Extended README.md with sections on dependency check, prompt.txt customization, and PTT usage.
- Tests: Added docstrings and type annotations, included a test for missing environment variables, removed invalid test cases.
- Performed code and security review and implemented recommendations.
- The IGNORED_USERS list can now be configured via the IGNORED_USERS environment variable in your .env file (comma-separated, case-insensitive). If not set, it defaults to {"saaromansbot", "streamelements"}. This allows you to easily adjust which users are ignored without changing the code.

## 1.1.1 (2025-04-18)
- Release version 1.1.1.
- No code changes; version bump for release management and documentation alignment.

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
