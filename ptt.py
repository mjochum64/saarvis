import threading
import os
from typing import Any, List
import tempfile
import logging
from pynput import mouse
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
from ai_responder import AIResponder

logging.basicConfig(level=logging.INFO)

class PTTRecorder:
    """Handles Push-to-Talk recording, transcription, AI response, and TTS playback.

    Usage:
        recorder = PTTRecorder()
        recorder.start_recording()
        # ...
        recorder.stop_recording()
    """
    def __init__(self) -> None:
        self.recording: bool = False
        self.frames: list[np.ndarray] = []
        self.stream: Any = None
        self.lock: threading.Lock = threading.Lock()

    def _callback(self, indata: np.ndarray, _frames: int, _time_info: Any, _status: Any) -> None:
        """Callback for sounddevice InputStream. Appends audio frames if recording."""
        if self.recording:
            with self.lock:
                self.frames.append(indata.copy())

    def start_recording(self) -> None:
        """Start audio recording using sounddevice InputStream."""
        if not self.recording:
            logging.info("Aufnahme gestartet...")
            self.frames = []
            self.stream = sd.InputStream(
                samplerate=16000,
                channels=1,
                callback=self._callback
            )
            self.stream.start()
            self.recording = True

    def stop_recording(self, filename: str = "aufnahme.wav") -> None:
        """Stop recording, save audio to file, and process transcription and AI response.

        Args:
            filename (str): Path to save the recorded WAV file.
        """
        if self.recording:
            logging.info("Aufnahme gestoppt. Speichere nach %s", filename)
            self.recording = False
            self.stream.stop()
            self.stream.close()
            audio = np.concatenate(self.frames, axis=0)
            wav.write(filename, 16000, audio)
            logging.info(f"Datei gespeichert: {filename}")
            self.handle_transcription_and_ai(filename)

    def handle_transcription_and_ai(self, filename: str) -> None:
        """Transcribes audio file, gets AI response, and plays TTS output.

        Args:
            filename (str): Path to the WAV file to transcribe.
        """
        try:
            from openai import OpenAI
        except ImportError:
            logging.error("Fehlende Abhängigkeit: openai. Bitte installiere mit 'pip install openai'.")
            return
        api_key = os.environ.get("OPENAI_API_KEY")
        model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        system_prompt = os.environ.get('OPENAI_SYSTEM_PROMPT', 'Du bist ein hilfreicher, freundlicher Chatbot für Twitch.').replace('\\n', '\n')
        system_prompt_file = os.environ.get('OPENAI_SYSTEM_PROMPT_FILE')
        logging.info("Transkribiere Audio mit Whisper...")
        client = OpenAI(api_key=api_key)
        with open(filename, "rb") as audio_file:
            try:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            except Exception as e:
                logging.error(f"Fehler bei der Transkription: {e}")
                return
        logging.info(f"Transkript: {transcript}")
        logging.info("Sende an KI...")
        ai = AIResponder(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            system_prompt_file=system_prompt_file
        )
        try:
            response = ai.get_response(transcript)
        except Exception as e:
            logging.error(f"Fehler bei der KI-Anfrage: {e}")
            return
        logging.info("KI-Antwort erhalten.")
        max_total_length = 500
        blocks = self.split_text_on_word_boundary(response, max_total_length)
        for block in blocks:
            logging.debug(f"TTS-Block: {block}")
            self.speak_text(block)

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
        blocks: List[str] = []
        current_block = ''
        for word in words:
            if current_block:
                if len(current_block) + 1 + len(word) > max_length:
                    blocks.append(current_block)
                    current_block = word
                else:
                    current_block += ' ' + word
            else:
                if len(word) > max_length:
                    blocks.append(word[:max_length])
                    current_block = word[max_length:]
                else:
                    current_block = word
        if current_block:
            blocks.append(current_block)
        return blocks

    def speak_text(self, text: str) -> None:
        """Converts text to speech using the ElevenLabs API and plays the resulting audio file.

        Args:
            text (str): The text to be spoken.
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
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file.write(response.content)
                tmp_file.flush()
                try:
                    import subprocess
                    subprocess.run(["mpg123", "-q", tmp_file.name], check=True)
                except Exception:
                    try:
                        subprocess.run(["mpv", "--quiet", tmp_file.name], check=True)
                    except Exception as e:
                        logging.error(f"Audioausgabe fehlgeschlagen: {e}")
                finally:
                    try:
                        os.remove(tmp_file.name)
                    except Exception as e:
                        logging.warning(f"Konnte TTS-Audiodatei nicht löschen: {e}")
        except Exception as exc:
            logging.error(f"TTS-Fehler: {exc}")

def ptt_listener_background() -> mouse.Listener:
    """Starts a background listener for Push-to-Talk (Mouse5) and returns the listener object."""
    recorder = PTTRecorder()
    def on_click(x: float, y: float, button: Any, pressed: bool) -> None:
        SUPPORTED_BUTTONS = (mouse.Button.button9,)
        if button in SUPPORTED_BUTTONS:
            if pressed:
                recorder.start_recording()
            else:
                recorder.stop_recording()
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    logging.info("PTT-Listener im Hintergrund gestartet (Maus5 für Aufnahme)")
    return listener
