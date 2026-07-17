"""
ai_service.py
-------------
Thin wrapper around the Groq API used for:
  1. Refining structured design briefs into rich image-generation prompts.
  2. Powering the conversational "AI Design Assistant" chatbot.

The module fails gracefully (returns a clear, non-crashing message) when
no API key is configured, so the rest of the app keeps working.
"""

from __future__ import annotations

import logging
from typing import Iterable

import streamlit as st

logger = logging.getLogger("ai_interior_designer")

DEFAULT_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT_ASSISTANT = (
    "You are 'Aura', the AI Design Assistant inside AI Interior Designer Pro. "
    "You are a warm, knowledgeable senior interior designer. You give practical, "
    "specific advice on: interior design ideas, furniture selection, color "
    "combinations, lighting design, budget planning, renovation strategy, Vastu "
    "Shastra, Feng Shui, space optimization, and storage solutions. Keep answers "
    "concise, structured with short paragraphs or bullet points, and always "
    "practical enough for someone to act on immediately."
)


def _get_api_key() -> str | None:
    try:
        return st.secrets.get("GROQ_API_KEY")  # type: ignore[union-attr]
    except Exception:  # secrets.toml may not exist locally
        pass
    import os

    return os.environ.get("GROQ_API_KEY")


def _get_model() -> str:
    try:
        model = st.secrets.get("GROQ_MODEL")  # type: ignore[union-attr]
        if model:
            return model
    except Exception:
        pass
    import os

    return os.environ.get("GROQ_MODEL", DEFAULT_MODEL)


def _get_client():
    """Lazily construct a Groq client. Returns None if no key is configured."""
    api_key = _get_api_key()
    if not api_key:
        return None
    try:
        from groq import Groq

        return Groq(api_key=api_key)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Failed to initialize Groq client: %s", exc)
        return None


def is_configured() -> bool:
    return _get_client() is not None


@st.cache_data(show_spinner=False, ttl=3600)
def refine_prompt(raw_prompt: str, instructions: str) -> str:
    """
    Send the structured design brief to Groq for refinement into a vivid,
    single-paragraph image generation prompt. Falls back to the raw prompt
    if no API key is configured or the call fails.
    """
    client = _get_client()
    if client is None:
        return raw_prompt

    try:
        response = client.chat.completions.create(
            model=_get_model(),
            messages=[
                {"role": "system", "content": "You are an expert prompt engineer for architectural visualization."},
                {"role": "user", "content": instructions},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        refined = response.choices[0].message.content.strip()
        return refined or raw_prompt
    except Exception as exc:
        logger.warning("Groq prompt refinement failed, using raw prompt: %s", exc)
        return raw_prompt


def chat_with_assistant(history: Iterable[dict[str, str]]) -> str:
    """
    Send full chat history (list of {"role": "user"/"assistant", "content": str})
    to Groq and return the assistant's reply. Returns a helpful fallback
    message if no API key is configured.
    """
    client = _get_client()
    if client is None:
        return (
            "⚠️ The AI Design Assistant needs a **GROQ_API_KEY** to respond. "
            "Add it to `.streamlit/secrets.toml` (or your `.env` file) and reload "
            "the app. In the meantime: for most rooms, aim for a 60/30/10 color "
            "split (dominant/secondary/accent), keep walkways at least 90cm wide, "
            "and layer three light sources (ambient, task, accent) for a "
            "professional finish."
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT_ASSISTANT}, *history]
    try:
        response = client.chat.completions.create(
            model=_get_model(),
            messages=messages,
            max_tokens=600,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.error("Groq chat call failed: %s", exc)
        return f"⚠️ The AI Design Assistant hit an error reaching Groq: `{exc}`. Please try again."
