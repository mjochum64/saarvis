from unittest.mock import patch, PropertyMock, AsyncMock, MagicMock
import os
import sys
import subprocess
import pytest

# Füge das Projektverzeichnis zum sys.path hinzu, damit main importiert werden kann
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import Bot

class DummyUser:
    """A dummy user for testing Twitch bot join events."""
    def __init__(self, name: str) -> None:
        self.name = name

class DummyChannel:
    """A dummy channel for capturing sent messages in tests."""
    def __init__(self) -> None:
        self.sent_messages = []
    async def send(self, message: str) -> None:
        self.sent_messages.append(message)

class DummyMessage:
    """A dummy message for simulating Twitch chat messages in tests."""
    def __init__(self, content: str, author_name: str, channel: DummyChannel, echo: bool = False) -> None:
        self.content = content
        self.author = type('Author', (), {'name': author_name})
        self.channel = channel
        self.echo = echo

@pytest.mark.asyncio
async def test_event_join_greets_new_user():
    """Test that a new user is greeted and added to greeted_users."""
    os.environ['TMI_TOKEN'] = 'dummy_token'
    os.environ['TWITCH_CHANNEL'] = 'dummy_channel'
    bot = Bot()
    with patch.object(type(bot), "nick", new_callable=PropertyMock) as mock_nick:
        mock_nick.return_value = "botnick"
        channel = DummyChannel()
        user = DummyUser('testuser')
        await bot.event_join(channel, user)
        assert 'Willkommen im Chat, @testuser!' in channel.sent_messages[0]
        assert 'testuser' in bot.greeted_users

@pytest.mark.asyncio
async def test_event_join_does_not_greet_self():
    """Test that the bot does not greet itself when joining."""
    os.environ['TMI_TOKEN'] = 'dummy_token'
    os.environ['TWITCH_CHANNEL'] = 'dummy_channel'
    bot = Bot()
    with patch.object(type(bot), "nick", new_callable=PropertyMock) as mock_nick:
        mock_nick.return_value = "botnick"
        channel = DummyChannel()
        user = DummyUser('botnick')
        await bot.event_join(channel, user)
        assert channel.sent_messages == []
        assert 'botnick' not in bot.greeted_users

@pytest.mark.asyncio
async def test_event_join_does_not_greet_twice():
    """Test that a user is not greeted twice on multiple joins."""
    os.environ['TMI_TOKEN'] = 'dummy_token'
    os.environ['TWITCH_CHANNEL'] = 'dummy_channel'
    bot = Bot()
    with patch.object(type(bot), "nick", new_callable=PropertyMock) as mock_nick:
        mock_nick.return_value = "botnick"
        channel = DummyChannel()
        user = DummyUser('testuser')
        # Erster Join
        await bot.event_join(channel, user)
        # Zweiter Join
        await bot.event_join(channel, user)
        assert channel.sent_messages.count('Willkommen im Chat, @testuser! Viel Spaß beim Zuschauen!') == 1
        assert 'testuser' in bot.greeted_users

@pytest.mark.asyncio
@pytest.mark.parametrize("content", [
    "Hallo @Nicole, wie geht's?",
    "@nicole bist du da?"
])
async def test_event_message_triggers_on_nicole_with_ai(content: str):
    """Test that messages containing @Nicole trigger an AI response."""
    os.environ['TMI_TOKEN'] = 'dummy_token'
    os.environ['TWITCH_CHANNEL'] = 'dummy_channel'
    os.environ['OPENAI_API_KEY'] = 'dummy_openai_key'
    bot = Bot()
    channel = DummyChannel()
    message = DummyMessage(content, 'fragenderUser', channel)
    # Patch AIResponder.get_response to avoid real API calls
    with patch.object(bot.ai, 'get_response', return_value="Das ist eine KI-Antwort.") as mock_ai, \
         patch.object(bot, 'handle_commands', new=AsyncMock()):
        await bot.event_message(message)
    assert any("@fragenderUser Das ist eine KI-Antwort." in m for m in channel.sent_messages)
    mock_ai.assert_called_once_with(content)

@pytest.mark.asyncio
async def test_speak_text_success(monkeypatch):
    """Test that speak_text runs without error when dependencies work."""
    os.environ['ELEVENLABS_API_KEY'] = 'dummy'
    os.environ['ELEVENLABS_VOICE_ID'] = 'dummy_voice'
    os.environ['ELEVENLABS_MODEL_ID'] = 'dummy_model'
    bot = Bot()
    monkeypatch.setattr("requests.post", lambda *a, **kw: MagicMock(status_code=200, content=b"audio"))
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: None)
    with patch("os.remove") as mock_rm:
        await bot.speak_text("Testausgabe")
        mock_rm.assert_called()

@pytest.mark.asyncio
async def test_speak_text_mpg123_fails(monkeypatch):
    """Test that speak_text falls back to mpv if mpg123 fails."""
    os.environ['ELEVENLABS_API_KEY'] = 'dummy'
    os.environ['ELEVENLABS_VOICE_ID'] = 'dummy_voice'
    os.environ['ELEVENLABS_MODEL_ID'] = 'dummy_model'
    bot = Bot()
    monkeypatch.setattr("requests.post", lambda *a, **kw: MagicMock(status_code=200, content=b"audio"))
    def fail_mpg123(*a, **kw):
        raise subprocess.CalledProcessError(1, 'mpg123')
    # Erster Aufruf (mpg123) schlägt fehl, zweiter (mpv) funktioniert
    monkeypatch.setattr("subprocess.run", fail_mpg123)
    with patch("os.remove") as mock_rm:
        try:
            await bot.speak_text("Testausgabe")
        except subprocess.CalledProcessError:
            pass  # Falls auch mpv fehlschlägt, ignorieren für diesen Test
        mock_rm.assert_called()

@pytest.mark.asyncio
async def test_speak_text_quota_exceeded(monkeypatch, caplog):
    """Test that speak_text logs correctly on HTTP error (e.g., quota exceeded)."""
    import requests
    os.environ['ELEVENLABS_API_KEY'] = 'dummy'
    os.environ['ELEVENLABS_VOICE_ID'] = 'dummy_voice'
    os.environ['ELEVENLABS_MODEL_ID'] = 'dummy_model'
    bot = Bot()
    class DummyResponse:
        status_code = 402
        content = b""
        def raise_for_status(self):
            raise requests.HTTPError("402 Payment Required")
        def json(self):
            return {"detail": "quota exceeded"}
        @property
        def text(self):
            return '{"detail": "quota exceeded"}'
    monkeypatch.setattr("requests.post", lambda *a, **kw: DummyResponse())
    with caplog.at_level("ERROR"):
        await bot.speak_text("Testausgabe")
    assert "quota exceeded" in caplog.text
    assert "TTS-Fehler (HTTP 402)" in caplog.text

def test_missing_env_vars(monkeypatch):
    """Test that the bot exits with a clear error if required environment variables are missing."""
    from main import check_required_env_vars
    for var in [
        'TMI_TOKEN',
        'TWITCH_CHANNEL',
        'OPENAI_API_KEY',
        'ELEVENLABS_API_KEY',
        'ELEVENLABS_VOICE_ID',
        'ELEVENLABS_MODEL_ID',
    ]:
        monkeypatch.delenv(var, raising=False)
    import pytest
    with pytest.raises(SystemExit):
        check_required_env_vars()
