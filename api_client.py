# api_client.py — Hugging Face Inference API integration.
# All HTTP communication and API error handling lives here.
# No UI or prompt engineering logic belongs in this module.

import io
import os
from typing import Optional

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

from config import FALLBACK_MODEL, PRIMARY_MODEL


# ---------------------------------------------------------------------------
# API Key Resolution
# ---------------------------------------------------------------------------

def _resolve_api_token() -> str:
    """
    Resolve the Hugging Face API token from available sources.

    Resolution order:
      1. Streamlit Secrets (production, Streamlit Community Cloud)
      2. Environment variable HF_API_TOKEN (local .env via python-dotenv)

    Raises:
        ValueError: If no token is found in any source.
    """
    # Attempt Streamlit Secrets first (only available when running inside Streamlit)
    try:
        import streamlit as st  # local import to avoid hard dependency at module level
        token = st.secrets.get("HF_API_TOKEN", "")
        if token:
            return token
    except Exception:
        pass  # Streamlit not running or secrets not configured

    # Fallback to environment variable (loaded from .env via python-dotenv)
    token = os.environ.get("HF_API_TOKEN", "")
    if token:
        return token

    raise ValueError(
        "Hugging Face API token not found. "
        "Set HF_API_TOKEN in your .env file (local) or Streamlit Secrets (deployed)."
    )


# ---------------------------------------------------------------------------
# Client Factory
# ---------------------------------------------------------------------------

def _build_client(token: str) -> InferenceClient:
    """Instantiate an InferenceClient with the provided token."""
    return InferenceClient(provider="hf-inference", api_key=token)


# ---------------------------------------------------------------------------
# Image Generation
# ---------------------------------------------------------------------------

def generate_image(
    prompt: str,
    negative_prompt: Optional[str] = None,
    width: int = 1024,
    height: int = 1024,
) -> bytes:
    """
    Generate an image from a text prompt using the Hugging Face Inference API.

    Attempts the primary model first. On failure, retries with the fallback model.
    Returns raw PNG/JPEG image bytes suitable for display or download.

    Args:
        prompt:          The fully constructed, style-conditioned prompt.
        negative_prompt: Optional negative prompt to guide generation away from unwanted elements.
        width:           Output image width in pixels.
        height:          Output image height in pixels.

    Returns:
        Raw image bytes (PIL Image serialised to bytes internally).

    Raises:
        RuntimeError: If both primary and fallback model calls fail.
        ValueError:   If the API token cannot be resolved.
    """
    token = _resolve_api_token()
    client = _build_client(token)

    kwargs: dict = {
        "prompt": prompt,
        "width": width,
        "height": height,
    }
    if negative_prompt and negative_prompt.strip():
        kwargs["negative_prompt"] = negative_prompt.strip()

    # Try primary model
    try:
        image = client.text_to_image(model=PRIMARY_MODEL, **kwargs)
        return _pil_to_bytes(image)
    except HfHubHTTPError as primary_error:
        primary_message = str(primary_error)

    # Retry with fallback model
    try:
        image = client.text_to_image(model=FALLBACK_MODEL, **kwargs)
        return _pil_to_bytes(image)
    except HfHubHTTPError as fallback_error:
        raise RuntimeError(
            f"Image generation failed on both models.\n"
            f"Primary ({PRIMARY_MODEL}): {primary_message}\n"
            f"Fallback ({FALLBACK_MODEL}): {fallback_error}"
        ) from fallback_error
    except Exception as unexpected:
        raise RuntimeError(
            f"Unexpected error during image generation: {unexpected}"
        ) from unexpected


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _pil_to_bytes(image) -> bytes:
    """
    Serialise a PIL Image object to raw PNG bytes.

    Args:
        image: A PIL.Image.Image instance returned by InferenceClient.

    Returns:
        Raw PNG-encoded bytes.
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


def validate_token() -> tuple[bool, str]:
    """
    Validate that the API token can be resolved without making an API call.

    Returns:
        (True, "") on success.
        (False, error_message) on failure.
    """
    try:
        _resolve_api_token()
        return True, ""
    except ValueError as e:
        return False, str(e)
