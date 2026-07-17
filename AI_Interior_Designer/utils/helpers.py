"""
helpers.py
----------
General-purpose helper functions: lightweight JSON-file persistence for
history/favorites (works out of the box on Streamlit Cloud's ephemeral
filesystem, with an in-session fallback), id generation, and formatting
utilities shared across pages.
"""

from __future__ import annotations

import base64
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

logger = logging.getLogger("ai_interior_designer")
logging.basicConfig(level=logging.INFO)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_FILE = DATA_DIR / "history.json"
FAVORITES_FILE = DATA_DIR / "favorites.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> list[dict[str, Any]]:
    _ensure_data_dir()
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return []


def _write_json(path: Path, data: list[dict[str, Any]]) -> None:
    _ensure_data_dir()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as exc:
        logger.warning("Could not write %s: %s", path, exc)


def new_id() -> str:
    """Generate a short unique identifier for a design record."""
    return uuid.uuid4().hex[:12]


def now_str() -> str:
    """Human-readable timestamp used for history/favorites entries."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def init_session_state() -> None:
    """Initialize all session_state keys used across the app, once per session."""
    defaults = {
        "history": _read_json(HISTORY_FILE),
        "favorites": _read_json(FAVORITES_FILE),
        "chat_messages": [],
        "dark_mode": True,
        "accent_color": "#7c5cff",
        "animations_enabled": True,
        "font_size": "Medium",
        "performance_mode": False,
        "image_quality": "High",
        "language": "English",
        "last_generated": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_to_history(record: dict[str, Any]) -> None:
    """Append a generated design record to history and persist it."""
    st.session_state.history.insert(0, record)
    st.session_state.history = st.session_state.history[:200]  # cap history size
    _write_json(HISTORY_FILE, st.session_state.history)


def toggle_favorite(record: dict[str, Any]) -> bool:
    """
    Add/remove a record from favorites by id. Returns True if now favorited,
    False if it was removed.
    """
    favs = st.session_state.favorites
    existing_ids = {f["id"] for f in favs}
    if record["id"] in existing_ids:
        st.session_state.favorites = [f for f in favs if f["id"] != record["id"]]
        _write_json(FAVORITES_FILE, st.session_state.favorites)
        return False
    favs.insert(0, record)
    st.session_state.favorites = favs
    _write_json(FAVORITES_FILE, favs)
    return True


def is_favorited(record_id: str) -> bool:
    return any(f["id"] == record_id for f in st.session_state.favorites)


def image_to_download_bytes(image_bytes: bytes) -> bytes:
    """Pass-through helper kept for a single, explicit download-prep step."""
    return image_bytes


def bytes_to_base64_data_uri(image_bytes: bytes, mime: str = "image/png") -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def truncate(text: str, length: int = 90) -> str:
    return text if len(text) <= length else text[: length - 1].rstrip() + "…"
