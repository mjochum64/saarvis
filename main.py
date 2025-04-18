import os
import dotenv
import logging
import requests
import tempfile
from ai_responder import AIResponder
from twitchio.ext import commands
import subprocess
from typing import List
import threading
from ptt import ptt_listener_background
import glob
import asyncio

class Bot(commands.Bot):
    """Twitch-Chatbot mit OpenAI- und ElevenLabs-TTS-Integration."""

    def __init__(self) -> None:
        """Initialisiert den Bot und lädt Konfigurationen aus Umgebungsvariablen."""
        super().__init__(
            token=os.environ['TMI_TOKEN'],
            prefix='!',
            initial_channels=[os.environ['TWITCH_CHANNEL']]
        )
        ignored_users_env = os.environ.get("IGNORED_USERS")
        if ignored_users_env:
            self.IGNORED_USERS = {u.strip().lower() for u in ignored_users_env.split(",") if u.strip()}
        else:
            self.IGNORED_USERS = {"saaromansbot", "streamelements"}
        self.greeted_users = set()
        self.ai = AIResponder(
            api_key=os.environ.get('OPENAI_API_KEY', ''),
            model=os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
            system_prompt=os.environ.get('OPENAI_SYSTEM_PROMPT', 'Du bist ein hilfreicher, freundlicher Chatbot für Twitch.').replace('\\n', '\n'),
            system_prompt_file=os.environ.get('OPENAI_SYSTEM_PROMPT_FILE')
        )
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
        self.KI_ACCESS_LEVEL = os.environ.get("KI_ACCESS_LEVEL", "all").lower()  # 'all', 'sub', 'follower'

    async def test_openai_connection(self) -> str:
        """Testet die Verbindung zur OpenAI-API und gibt eine Statusmeldung zurück.

        Returns:
            str: Statusmeldung zur OpenAI-API.
        """
        try:
            response = self.ai.get_response("ping", max_tokens=5)
            if response and "Entschuldigung" not in response:
                return "OpenAI-Schnittstelle erreichbar."
            return "OpenAI-Schnittstelle antwortet nicht wie erwartet."
        except requests.RequestException as exc:
            logging.error("OpenAI-Statusprüfung fehlgeschlagen: %s", exc)
            return f"OpenAI-Schnittstelle FEHLER: {exc}"

    async def event_ready(self) -> None:
        """Wird aufgerufen, wenn der Bot erfolgreich verbunden ist."""
        print(f'Logged in as | {self.nick}')
        status = await self.test_openai_connection()
        print(f'[OpenAI-Status] {status}')

    async def event_join(self, channel, user) -> None:
        """Begrüßt neue Nutzer im Chat."""
        if user.name.lower() != self.nick.lower() and user.name not in self.greeted_users:
            await channel.send(f"Willkommen im Chat, @{user.name}! Viel Spaß beim Zuschauen!")
            self.greeted_users.add(user.name)

    @staticmethod
    def split_text_on_word_boundary(text: str, max_length: int) -> List[str]:
        """Splits text into blocks of up to max_length characters, breaking only at word boundaries.

        Args:
            text (str): The text to split.
            max_length (int): Maximum length of each block.

        Returns:
            List[str]: List of text blocks, each not exceeding max_length and not splitting words.
        """
        words = text.split()
        blocks = []
        current_block = ''
        for word in words:
            if current_block:
                # +1 for the space
                if len(current_block) + 1 + len(word) > max_length:
                    blocks.append(current_block)
                    current_block = word
                else:
                    current_block += ' ' + word
            else:
                if len(word) > max_length:
                    # If a single word is longer than max_length, split it hard
                    blocks.append(word[:max_length])
                    current_block = word[max_length:]
                else:
                    current_block = word
        if current_block:
            blocks.append(current_block)
        return blocks

    async def speak_text(self, text: str) -> None:
        """
        Converts text to speech using the ElevenLabs API and plays the resulting audio file.

        Args:
            text (str): The text to be spoken.

        Raises:
            requests.RequestException: If a network or API error occurs.
            IOError: If audio file handling fails.

        Notes:
            - The timeout for the ElevenLabs API request is set to 60 seconds to support longer texts.
            - For best reliability, keep texts reasonably short (e.g., <1000 characters).
            - If a timeout occurs, a clear error is logged and the user is advised to shorten the text.
        """
        api_key = os.environ.get('ELEVENLABS_API_KEY', 'PLACEHOLDER_API_KEY')
        voice_id = os.environ.get('ELEVENLABS_VOICE_ID', 'tKmESGVo91DcC5kFPRS6')
        model_id = os.environ.get('ELEVENLABS_MODEL_ID', 'eleven_multilingual_v2')
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {"stability": 0.75, "similarity_boost": 0.25}
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            try:
                response.raise_for_status()
            except requests.HTTPError as http_exc:
                error_detail = None
                try:
                    error_json = response.json()
                    error_detail = error_json.get('detail') or error_json.get('message') or str(error_json)
                except ValueError:
                    error_detail = response.text
                logging.error(
                    "TTS-Fehler (HTTP %s): %s | Detail: %s", response.status_code, http_exc, error_detail
                )
                return
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file.write(response.content)
                tmp_file.flush()
                logging.info("TTS-Audiodatei gespeichert: %s", tmp_file.name)
                try:
                    subprocess.run(["mpg123", "-q", tmp_file.name], check=True)
                except subprocess.CalledProcessError as mpg_exc:
                    logging.warning("mpg123 fehlgeschlagen: %s, versuche mpv", mpg_exc)
                    try:
                        subprocess.run(["mpv", "--quiet", tmp_file.name], check=True)
                    except subprocess.CalledProcessError as mpv_exc:
                        logging.error("mpv fehlgeschlagen: %s", mpv_exc)
                finally:
                    try:
                        os.remove(tmp_file.name)
                        logging.info("TTS-Audiodatei gelöscht: %s", tmp_file.name)
                    except OSError as rm_exc:
                        logging.warning("Konnte TTS-Audiodatei nicht löschen: %s", rm_exc)
        except requests.Timeout:
            logging.error("TTS-Fehler: Die Anfrage an ElevenLabs hat das Timeout überschritten (60s). Text ggf. kürzen oder später erneut versuchen.")
        except (requests.RequestException, IOError) as exc:
            logging.error("TTS-Fehler: %s", exc)

    async def is_follower(self, user_name: str) -> bool:
        """Check if a user is a follower of the channel using the Twitch Helix API.

        Args:
            user_name (str): The username to check.
        Returns:
            bool: True if the user is a follower, False otherwise.
        """
        import aiohttp
        channel = os.environ["TWITCH_CHANNEL"].lower()
        client_id = os.environ.get("CLIENT_ID")
        access_token = os.environ.get("TMI_TOKEN")
        if not client_id or not access_token:
            logging.warning("CLIENT_ID or TMI_TOKEN missing for follower check.")
            return False
        # Get user and channel IDs
        headers = {"Client-ID": client_id, "Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            # Get channel user ID
            async with session.get(f"https://api.twitch.tv/helix/users?login={channel}", headers=headers) as resp:
                data = await resp.json()
                if not data.get("data"):
                    return False
                channel_id = data["data"][0]["id"]
            # Get user ID
            async with session.get(f"https://api.twitch.tv/helix/users?login={user_name}", headers=headers) as resp:
                data = await resp.json()
                if not data.get("data"):
                    return False
                user_id = data["data"][0]["id"]
            # Check if user follows channel
            url = f"https://api.twitch.tv/helix/users/follows?from_id={user_id}&to_id={channel_id}"
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                return data.get("total", 0) > 0

    async def event_message(self, message) -> None:
        """Reagiert auf Nachrichten mit @Nicole und gibt eine KI-Antwort mit TTS aus.

        Die Antwort wird in Blöcke von maximal 500 Zeichen aufgeteilt, wobei der Username-Prefix beim ersten Block mitgerechnet wird.
        Die Trennung erfolgt nur an Wortgrenzen.
        
        Args:
            message: Die empfangene Twitch-Chatnachricht.
        """
        if message.echo:
            return
        # Ignore messages from certain users (e.g. bots)
        if message.author.name.lower() in self.IGNORED_USERS:
            return
        content = message.content.lower()
        if "@nicole" in content:
            # KI-Zugriffsprüfung
            access = self.KI_ACCESS_LEVEL
            is_sub = getattr(message.author, "is_subscriber", False)
            is_follower = True
            channel_owner = os.environ.get("TWITCH_CHANNEL", "").lower()
            is_owner = message.author.name.lower() == channel_owner
            if not is_owner:
                if access == "sub" and not is_sub:
                    await message.channel.send(f"@{message.author.name} KI-Antworten sind nur für Abonnenten verfügbar.")
                    return
                if access == "follower":
                    is_follower = await self.is_follower(message.author.name)
                    if not is_follower:
                        await message.channel.send(f"@{message.author.name} KI-Antworten sind nur für Follower verfügbar.")
                        return
                if access not in ("all", "sub", "follower"):
                    await message.channel.send("KI access misconfigured. Allowed: all, sub, follower.")
                    return
            prompt = message.content
            ai_reply = self.ai.get_response(prompt)
            max_total_length = 500
            prefix = f"@{message.author.name} "
            # Ersten Block so splitten, dass prefix+block <= 500
            first_block_max = max_total_length - len(prefix)
            blocks = self.split_text_on_word_boundary(ai_reply, first_block_max)
            if blocks:
                first_block = blocks[0]
                await message.channel.send(f"{prefix}{first_block}")
                # Restliche Blöcke ggf. weiter splitten (ohne Prefix, max 500)
                rest = ' '.join(blocks[1:])
                if rest:
                    rest_blocks = self.split_text_on_word_boundary(rest, max_total_length)
                    for block in rest_blocks:
                        await message.channel.send(block)
            await self.speak_text(ai_reply)
            return
        await self.handle_commands(message)

    async def send_ptt_message(self, text: str) -> None:
        """Sendet einen Textblock aus der PTT-Funktion in den Twitch-Chat.

        Args:
            text (str): Der zu sendende Textblock.
        """
        # Sende in den ersten initial_channel
        if self.connected_channels:
            try:
                await self.connected_channels[0].send(text)
            except Exception as exc:
                logging.error("Fehler beim Senden der PTT-Nachricht: %s", exc)
        else:
            logging.warning("Keine verbundenen Kanäle für PTT-Chat-Ausgabe.")

def cleanup_temp_audio_files() -> None:
    """Removes leftover temporary audio files (*.mp3, aufnahme.wav) from the working directory.

    This should be called at program startup to prevent disk space issues from old files.
    """
    patterns = ["*.mp3", "aufnahme.wav"]
    for pattern in patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                logging.info("Removed leftover audio file: %s", file_path)
            except Exception as exc:
                logging.warning("Could not remove %s: %s", file_path, exc)

def check_required_env_vars() -> None:
    """Checks for required environment variables and exits if any are missing.

    Raises:
        SystemExit: If a required environment variable is missing.
    """
    required_vars = [
        'TMI_TOKEN',
        'TWITCH_CHANNEL',
        'OPENAI_API_KEY',
        'ELEVENLABS_API_KEY',
        'ELEVENLABS_VOICE_ID',
        'ELEVENLABS_MODEL_ID',
    ]
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        missing_str = ', '.join(missing)
        logging.critical("Missing required environment variables: %s. Please set them in your .env file.", missing_str)
        raise SystemExit(1)

if __name__ == "__main__":
    dotenv.load_dotenv()
    cleanup_temp_audio_files()
    check_required_env_vars()
    bot = Bot()
    # PTT-Listener im Hintergrund starten, Chat-Callback übergeben
    def ptt_chat_callback(text: str):
        # Thread-sicheres Aufrufen der async-Methode aus dem PTT-Thread
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            asyncio.run_coroutine_threadsafe(bot.send_ptt_message(text), loop)
        else:
            # Fallback: neuen Loop starten (sollte im Normalfall nicht nötig sein)
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(bot.send_ptt_message(text))
    threading.Thread(target=ptt_listener_background, args=(ptt_chat_callback,), daemon=True).start()
    bot.run()