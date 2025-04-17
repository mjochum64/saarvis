"""AIResponder: Handles communication with the OpenAI API for chat responses.

This module provides the AIResponder class, which can be used to send prompts to the OpenAI API and receive generated responses. It is designed for integration with chatbots and other conversational agents.

PEP 8/PEP 257-konform, mit Fehlerbehandlung und Logging.
"""
import openai
import logging
import os

class AIResponder:
    """Handles communication with the OpenAI API for chat responses."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", system_prompt: str = None, system_prompt_file: str = None):
        """
        Args:
            api_key (str): OpenAI API key.
            model (str): OpenAI chat model to use.
            system_prompt (str, optional): System prompt for the AI session.
            system_prompt_file (str, optional): Path to a file containing the system prompt.
        """
        self.api_key = api_key
        self.model = model
        prompt = None
        if system_prompt_file:
            try:
                with open(system_prompt_file, "r", encoding="utf-8") as f:
                    prompt = f.read().strip()
            except FileNotFoundError as e:
                logging.error("Fehler beim Laden des System-Prompts aus Datei: %s", e)
        self.system_prompt = prompt or system_prompt or "Du bist ein hilfreicher, freundlicher Chatbot für Twitch."
        self.max_tokens = int(os.environ.get("OPENAI_MAX_TOKENS", 100))
        openai.api_key = api_key

    def get_response(self, prompt: str, max_tokens: int = None, temperature: float = 0.7) -> str:
        """
        Sends a prompt to the OpenAI API and returns the response.

        Args:
            prompt (str): The user's message.
            max_tokens (int, optional): Maximum number of tokens in the response. Defaults to value from environment.
            temperature (float): Sampling temperature.

        Returns:
            str: The AI-generated response.
        """
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
                temperature=temperature,
            )
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug("OpenAI API response: %r", response)
            return response.choices[0].message.content.strip()
        except openai.OpenAIError as e:
            logging.error("OpenAI API error: %s", e)
            return "Entschuldigung, ich kann gerade nicht antworten."
        except Exception as e:
            logging.error("Unerwarteter Fehler: %s", e)
            return "Entschuldigung, ein unerwarteter Fehler ist aufgetreten."
