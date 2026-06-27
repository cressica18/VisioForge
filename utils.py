# utils.py — Utility functions: session history, image helpers, formatting.
# No UI rendering, API calls, or prompt engineering belongs here.

import base64
import random
import uuid
from datetime import datetime
from typing import Optional

import streamlit as st

from config import (
    MAX_HISTORY_ITEMS,
    RANDOM_PROMPTS,
    SESSION_HISTORY_KEY,
    SESSION_LAST_IMAGE_KEY,
    SESSION_LAST_META_KEY,
)


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

def _make_generation_record(
    prompt: str,
    style: str,
    final_prompt: str,
    image_bytes: bytes,
    image_size: str,
) -> dict:
    """
    Construct a generation history record dictionary.

    Args:
        prompt:       The raw user-entered prompt.
        style:        The selected style name.
        final_prompt: The fully styled prompt sent to the API.
        image_bytes:  Raw PNG bytes of the generated image.
        image_size:   Human-readable size label (e.g. "Square (1024 × 1024)").

    Returns:
        A dictionary conforming to the session history schema.
    """
    return {
        "id": str(uuid.uuid4()),
        "prompt": prompt,
        "style": style,
        "final_prompt": final_prompt,
        "image_bytes": image_bytes,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_size": image_size,
    }


# ---------------------------------------------------------------------------
# Session State Management
# ---------------------------------------------------------------------------

def init_session_state() -> None:
    """Initialise all required Streamlit session state keys if not already set."""
    if SESSION_HISTORY_KEY not in st.session_state:
        st.session_state[SESSION_HISTORY_KEY] = []
    if SESSION_LAST_IMAGE_KEY not in st.session_state:
        st.session_state[SESSION_LAST_IMAGE_KEY] = None
    if SESSION_LAST_META_KEY not in st.session_state:
        st.session_state[SESSION_LAST_META_KEY] = None
    # Separate value store for the prompt text area.
    # Streamlit forbids writing to a widget's own key after it renders,
    # so the Random Prompt button writes here and the text_area reads it via value=.
    if "prompt_value" not in st.session_state:
        st.session_state["prompt_value"] = ""


def add_to_history(
    prompt: str,
    style: str,
    final_prompt: str,
    image_bytes: bytes,
    image_size: str,
) -> dict:
    """
    Add a completed generation to session history and update the last-result state.

    Maintains a rolling window of MAX_HISTORY_ITEMS to avoid unbounded memory growth.

    Returns:
        The newly created history record.
    """
    record = _make_generation_record(prompt, style, final_prompt, image_bytes, image_size)

    history: list = st.session_state[SESSION_HISTORY_KEY]
    history.insert(0, record)

    # Trim to rolling window
    if len(history) > MAX_HISTORY_ITEMS:
        st.session_state[SESSION_HISTORY_KEY] = history[:MAX_HISTORY_ITEMS]

    st.session_state[SESSION_LAST_IMAGE_KEY] = image_bytes
    st.session_state[SESSION_LAST_META_KEY] = record

    return record


def get_history() -> list[dict]:
    """Return the current generation history list from session state."""
    return st.session_state.get(SESSION_HISTORY_KEY, [])


def clear_history() -> None:
    """Clear all generation history and reset the last-result state."""
    st.session_state[SESSION_HISTORY_KEY] = []
    st.session_state[SESSION_LAST_IMAGE_KEY] = None
    st.session_state[SESSION_LAST_META_KEY] = None


def get_last_image() -> Optional[bytes]:
    """Return the most recently generated image bytes, or None."""
    return st.session_state.get(SESSION_LAST_IMAGE_KEY)


def get_last_metadata() -> Optional[dict]:
    """Return the metadata record for the most recent generation, or None."""
    return st.session_state.get(SESSION_LAST_META_KEY)


# ---------------------------------------------------------------------------
# Image Helpers
# ---------------------------------------------------------------------------

def image_to_base64(image_bytes: bytes) -> str:
    """Encode raw image bytes as a base64 string (for HTML embedding)."""
    return base64.b64encode(image_bytes).decode("utf-8")


def build_download_filename(prompt: str, style: str) -> str:
    """
    Construct a clean filename for image downloads.

    Uses the first three words of the prompt and the style name,
    joined with underscores and suffixed with .png.

    Args:
        prompt: The user's original prompt text.
        style:  The selected style name.

    Returns:
        A sanitised filename string, e.g. "futuristic_indian_city_Cyberpunk.png"
    """
    words = prompt.strip().split()[:3]
    slug = "_".join(word.strip(".,!?\"'") for word in words).lower()
    style_slug = style.replace(" ", "_")
    return f"{slug}_{style_slug}.png"


# ---------------------------------------------------------------------------
# Random Prompt
# ---------------------------------------------------------------------------

def get_random_prompt() -> str:
    """Return a randomly selected creative seed prompt."""
    return random.choice(RANDOM_PROMPTS)


# ---------------------------------------------------------------------------
# Remix Helper
# ---------------------------------------------------------------------------

def build_remix_prompt(original_prompt: str, new_style: str) -> str:
    """
    Prepare a remix by returning the original subject prompt unchanged.
    The caller is responsible for applying the new style via build_styled_prompt.

    Args:
        original_prompt: The user's raw subject prompt from a previous generation.
        new_style:       The style the user wants to remix into (unused here, passed
                         for logging or future extension).

    Returns:
        The original raw prompt, stripped of whitespace.
    """
    return original_prompt.strip()


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def truncate(text: str, max_chars: int = 60) -> str:
    """Truncate a string to max_chars, appending '…' if truncated."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"


def format_timestamp(raw: str) -> str:
    """
    Reformat a stored timestamp string to a friendlier display format.

    Input:  "2024-07-15 14:32:08"
    Output: "Jul 15, 2024 at 14:32"
    """
    try:
        dt = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %Y at %H:%M")
    except ValueError:
        return raw
