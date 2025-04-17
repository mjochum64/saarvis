"""AIResponder: Handles communication with the OpenAI API for chat responses.

This module provides the AIResponder class, which can be used to send prompts to the OpenAI API and receive generated responses. It is designed for integration with chatbots and other conversational agents.

PEP 8/PEP 257-konform, mit Fehlerbehandlung und Logging.
"""
import openai
import logging
import os
from typing import Optional

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
            except Exception as e:
                logging.error(f"Fehler beim Laden des System-Prompts aus Datei: {e}")
        self.system_prompt = prompt or system_prompt or "Du bist ein hilfreicher, freundlicher Chatbot für Twitch."
        openai.api_key = api_key

    def get_response(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """
        Sends a prompt to the OpenAI API and returns the response.

        Args:
            prompt (str): The user's message.
            max_tokens (int): Maximum number of tokens in the response.
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
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return "Entschuldigung, ich kann gerade nicht antworten."
