import os
import dotenv
import logging
import requests
import tempfile
from ai_responder import AIResponder
from twitchio.ext import commands
import subprocess
from typing import List

class Bot(commands.Bot):
    """Twitch-Chatbot mit OpenAI- und ElevenLabs-TTS-Integration."""

    def __init__(self) -> None:
        """Initialisiert den Bot und lädt Konfigurationen aus Umgebungsvariablen."""
        super().__init__(
            token=os.environ['TMI_TOKEN'],
            prefix='!',
            initial_channels=[os.environ['TWITCH_CHANNEL']]
        )
        self.greeted_users = set()
        self.ai = AIResponder(
            api_key=os.environ.get('OPENAI_API_KEY', ''),
            model=os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
            system_prompt=os.environ.get('OPENAI_SYSTEM_PROMPT', 'Du bist ein hilfreicher, freundlicher Chatbot für Twitch.').replace('\\n', '\n'),
            system_prompt_file=os.environ.get('OPENAI_SYSTEM_PROMPT_FILE')
        )
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logging.basicConfig(level=getattr(logging, log_level, logging.INFO))

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
                except Exception:
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

    async def event_message(self, message) -> None:
        """Reagiert auf Nachrichten mit @Nicole oder /Nicole und gibt eine KI-Antwort mit TTS aus.

        Die Antwort wird in Blöcke von maximal 500 Zeichen aufgeteilt, wobei der Username-Prefix beim ersten Block mitgerechnet wird.
        Die Trennung erfolgt nur an Wortgrenzen.
        
        Args:
            message: Die empfangene Twitch-Chatnachricht.
        """
        if message.echo:
            return
        content = message.content.lower()
        if ("@nicole" in content) or content.startswith("/nicole"):
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

if __name__ == "__main__":
    dotenv.load_dotenv()
    bot = Bot()
    bot.run()