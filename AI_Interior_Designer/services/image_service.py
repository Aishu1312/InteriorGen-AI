"""
image_service.py
-----------------
Modular image generation service. Swapping providers requires changing
ONLY the `IMAGE_PROVIDER` config value (via st.secrets or environment
variable) — no other code needs to change.

Supported providers:
    - "demo"        : No API key needed. Renders a styled, labeled
                      placeholder mockup locally with Pillow so the full
                      app experience (gallery, history, downloads, before/
                      after slider) works out of the box on first deploy.
    - "huggingface" : Hugging Face Inference API (e.g. FLUX, SDXL).
    - "stability"   : Stability AI's text-to-image REST API.
    - "replicate"   : Replicate's prediction API.
    - "fal"         : Fal.ai's text-to-image API.

To add a new provider: implement a `_generate_with_<name>(prompt) -> bytes`
function and register it in the `_PROVIDERS` dict at the bottom of this file.
"""

from __future__ import annotations

import io
import logging
import os
import textwrap
import time
from typing import Callable

import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFilter, ImageFont

logger = logging.getLogger("ai_interior_designer")


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------
def _get_config(key: str, default: str = "") -> str:
    try:
        value = st.secrets.get(key)  # type: ignore[union-attr]
        if value:
            return value
    except Exception:
        pass
    return os.environ.get(key, default)


def get_provider_name() -> str:
    return _get_config("IMAGE_PROVIDER", "demo").lower()


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------
def _generate_with_demo(prompt: str) -> bytes:
    """
    Render an attractive, deterministic placeholder "mockup" image so the
    whole application is demoable without any external API key. Colors are
    derived from the prompt text so different prompts look visually distinct.
    """
    width, height = 1024, 683
    seed = sum(ord(c) for c in prompt) or 1

    palette_options = [
        ((30, 24, 55), (124, 92, 255)),
        ((20, 30, 40), (232, 195, 122)),
        ((35, 20, 30), (255, 122, 198)),
        ((18, 28, 26), (120, 200, 170)),
        ((28, 22, 18), (222, 160, 100)),
    ]
    base_color, accent_color = palette_options[seed % len(palette_options)]

    img = Image.new("RGB", (width, height), base_color)
    draw = ImageDraw.Draw(img)

    # Soft diagonal gradient bands to suggest window light / architecture
    for i in range(0, width, 6):
        t = i / width
        blended = tuple(int(base_color[c] + (accent_color[c] - base_color[c]) * t * 0.35) for c in range(3))
        draw.line([(i, 0), (0, i * height / width if width else 0)], fill=blended, width=6)

    img = img.filter(ImageFilter.GaussianBlur(2))
    draw = ImageDraw.Draw(img)

    # Simple "room" silhouette: floor, back wall, window
    draw.rectangle([0, height * 0.68, width, height], fill=tuple(int(c * 0.55) for c in accent_color))
    draw.rectangle(
        [width * 0.62, height * 0.18, width * 0.92, height * 0.62],
        fill=tuple(min(255, int(c * 1.3)) for c in accent_color),
    )
    draw.rectangle([width * 0.1, height * 0.45, width * 0.42, height * 0.68], outline=accent_color, width=4)

    # Centered label card
    card_w, card_h = int(width * 0.72), 150
    card_x, card_y = (width - card_w) // 2, height - card_h - 40
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=22,
        fill=(15, 15, 26, 190),
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    label = "DEMO PREVIEW — connect an image API for real renders"
    wrapped = textwrap.fill(prompt, width=70)
    draw.text((card_x + 24, card_y + 16), label, fill=(232, 195, 122), font=font)
    draw.text((card_x + 24, card_y + 40), wrapped[:220], fill=(244, 242, 255), font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _generate_with_huggingface(prompt: str) -> bytes:
    api_key = _get_config("HF_API_KEY")
    model = _get_config("HF_MODEL", "black-forest-labs/FLUX.1-schnell")
    if not api_key:
        raise RuntimeError("HF_API_KEY is not configured.")

    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"Hugging Face API error {response.status_code}: {response.text[:200]}")
    return response.content


def _generate_with_stability(prompt: str) -> bytes:
    api_key = _get_config("STABILITY_API_KEY")
    if not api_key:
        raise RuntimeError("STABILITY_API_KEY is not configured.")

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "image/*"}
    files = {"none": ""}
    data = {"prompt": prompt, "output_format": "png"}
    response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"Stability API error {response.status_code}: {response.text[:200]}")
    return response.content


def _generate_with_replicate(prompt: str) -> bytes:
    api_token = _get_config("REPLICATE_API_TOKEN")
    version = _get_config("REPLICATE_MODEL_VERSION")
    if not api_token or not version:
        raise RuntimeError("REPLICATE_API_TOKEN / REPLICATE_MODEL_VERSION not configured.")

    headers = {"Authorization": f"Token {api_token}", "Content-Type": "application/json"}
    create_resp = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers=headers,
        json={"version": version, "input": {"prompt": prompt}},
        timeout=30,
    )
    create_resp.raise_for_status()
    prediction = create_resp.json()
    get_url = prediction["urls"]["get"]

    for _ in range(60):
        poll = requests.get(get_url, headers=headers, timeout=30).json()
        status = poll.get("status")
        if status == "succeeded":
            output = poll["output"]
            image_url = output[0] if isinstance(output, list) else output
            return requests.get(image_url, timeout=60).content
        if status == "failed":
            raise RuntimeError(f"Replicate prediction failed: {poll.get('error')}")
        time.sleep(2)

    raise RuntimeError("Replicate prediction timed out.")


def _generate_with_fal(prompt: str) -> bytes:
    api_key = _get_config("FAL_API_KEY")
    if not api_key:
        raise RuntimeError("FAL_API_KEY is not configured.")

    url = "https://fal.run/fal-ai/flux/schnell"
    headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json={"prompt": prompt}, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"Fal.ai API error {response.status_code}: {response.text[:200]}")
    payload = response.json()
    image_url = payload["images"][0]["url"]
    return requests.get(image_url, timeout=60).content


_PROVIDERS: dict[str, Callable[[str], bytes]] = {
    "demo": _generate_with_demo,
    "huggingface": _generate_with_huggingface,
    "stability": _generate_with_stability,
    "replicate": _generate_with_replicate,
    "fal": _generate_with_fal,
}


def generate_image(prompt: str) -> tuple[bytes, str | None]:
    """
    Generate an image for the given prompt using the configured provider.

    Returns a tuple of (image_bytes, error_message). error_message is None
    on success; if a configured external provider fails, the function
    automatically falls back to the demo renderer and returns an
    explanatory error message alongside the fallback image.
    """
    provider = get_provider_name()
    generator = _PROVIDERS.get(provider, _generate_with_demo)

    if provider == "demo":
        return _generate_with_demo(prompt), None

    try:
        return generator(prompt), None
    except Exception as exc:
        logger.error("Image provider '%s' failed: %s", provider, exc)
        fallback = _generate_with_demo(prompt)
        error_message = (
            f"⚠️ The '{provider}' image provider could not generate an image ({exc}). "
            "Showing a demo placeholder instead — check your API key/config."
        )
        return fallback, error_message
