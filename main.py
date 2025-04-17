import os
import dotenv
import logging
import requests
import tempfile
from ai_responder import AIResponder
from twitchio.ext import commands
import subprocess
from typing import Optional

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
        logging.basicConfig(level=logging.INFO)

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
        except Exception as exc:
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

    async def speak_text(self, text: str) -> None:
        """
        Wandelt Text mittels ElevenLabs API in Sprache um und spielt die Audiodatei ab.

        Args:
            text (str): Der zu sprechende Text.
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
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
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
                    except Exception as rm_exc:
                        logging.warning("Konnte TTS-Audiodatei nicht löschen: %s", rm_exc)
        except (requests.RequestException, IOError) as exc:
            logging.error("TTS-Fehler: %s", exc)

    async def event_message(self, message) -> None:
        """Reagiert auf Nachrichten mit @Nicole oder /Nicole und gibt eine KI-Antwort mit TTS aus."""
        if message.echo:
            return
        content = message.content.lower()
        if ("@nicole" in content) or content.startswith("/nicole"):
            prompt = message.content
            ai_reply = self.ai.get_response(prompt)
            await message.channel.send(f"@{message.author.name} {ai_reply}")
            await self.speak_text(ai_reply)
            return
        await self.handle_commands(message)

if __name__ == "__main__":
    dotenv.load_dotenv()
    bot = Bot()
    bot.run()