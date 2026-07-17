"""
Modular, production-grade image generation service with robust error handling,
exponential backoff, and automatic provider fallback.
"""
from __future__ import annotations

import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Callable

import requests
import streamlit as st
import fal_client
import replicate
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger("ai_interior_designer")


def _get_config(key: str, default: str = "") -> str:
    try:
        value = st.secrets.get(key)
        if value:
            return value
    except Exception:
        pass
    return os.environ.get(key, default)


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class AuthError(ProviderError):
    """Authentication or invalid key error."""
    pass


class RateLimitError(ProviderError):
    """Rate limit or quota exceeded error."""
    pass


class NetworkError(ProviderError):
    """Network, DNS, or server error."""
    pass


def log_attempt(retry_state):
    logger.warning(
        f"Retrying {retry_state.fn.__name__} after {retry_state.attempt_number} attempts "
        f"due to: {retry_state.outcome.exception()}"
    )


class BaseProvider(ABC):
    def __init__(self):
        self.name = self.__class__.__name__.replace("Provider", "")

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        pass

    @abstractmethod
    def _generate(self, prompt: str) -> bytes:
        pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=(
            retry_if_exception_type(requests.exceptions.RequestException)
            | retry_if_exception_type(RateLimitError)
            | retry_if_exception_type(NetworkError)
        ),
        before_sleep=log_attempt,
        reraise=True,
    )
    def generate_image(self, prompt: str) -> bytes:
        logger.info(f"[{self.name}] Attempting generation...")
        start_time = time.time()
        try:
            result = self._generate(prompt)
            duration = time.time() - start_time
            logger.info(f"[{self.name}] Generation successful in {duration:.2f}s")
            return result
        except Exception as e:
            logger.error(f"[{self.name}] Generation failed: {type(e).__name__} - {str(e)}")
            raise


class FalProvider(BaseProvider):
    @property
    def is_configured(self) -> bool:
        return bool(_get_config("FAL_API_KEY"))

    def _generate(self, prompt: str) -> bytes:
        api_key = _get_config("FAL_API_KEY")
        os.environ["FAL_KEY"] = api_key
        try:
            result = fal_client.subscribe("fal-ai/flux/schnell", arguments={"prompt": prompt}, with_logs=True)
            image_url = result["images"][0]["url"]
            return requests.get(image_url, timeout=30).content
        except Exception as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                raise AuthError(f"Fal authentication failed: {e}")
            raise NetworkError(f"Fal generation failed: {e}")


class ReplicateProvider(BaseProvider):
    @property
    def is_configured(self) -> bool:
        return bool(_get_config("REPLICATE_API_TOKEN"))

    def _generate(self, prompt: str) -> bytes:
        api_token = _get_config("REPLICATE_API_TOKEN")
        version = _get_config("REPLICATE_MODEL_VERSION", "black-forest-labs/flux-schnell")

        client = replicate.Client(api_token=api_token)
        try:
            output = client.run(version, input={"prompt": prompt})
            image_url = output[0] if isinstance(output, list) else output
            return requests.get(image_url, timeout=30).content
        except replicate.exceptions.ReplicateError as e:
            if e.status == 401:
                raise AuthError(f"Replicate authentication failed: {e}")
            if e.status == 429:
                raise RateLimitError(f"Replicate rate limit exceeded: {e}")
            raise NetworkError(f"Replicate error: {e}")
        except Exception as e:
            raise NetworkError(f"Replicate generation failed: {e}")


class HuggingFaceProvider(BaseProvider):
    @property
    def is_configured(self) -> bool:
        return bool(_get_config("HF_API_KEY"))

    def _generate(self, prompt: str) -> bytes:
        api_key = _get_config("HF_API_KEY")
        model = _get_config("HF_MODEL", "black-forest-labs/FLUX.1-schnell")
        url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)
            if response.status_code == 401:
                raise AuthError("Invalid Hugging Face API key")
            if response.status_code == 429:
                raise RateLimitError("Hugging Face rate limit exceeded")
            if response.status_code == 503:
                raise NetworkError("Model is currently loading")
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Hugging Face network error: {e}")


class StabilityProvider(BaseProvider):
    @property
    def is_configured(self) -> bool:
        return bool(_get_config("STABILITY_API_KEY"))

    def _generate(self, prompt: str) -> bytes:
        api_key = _get_config("STABILITY_API_KEY")
        url = "https://api.stability.ai/v2beta/stable-image/generate/core"
        headers = {"Authorization": f"Bearer {api_key}", "Accept": "image/*"}
        files = {"none": ""}
        data = {"prompt": prompt, "output_format": "png"}

        try:
            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            if response.status_code == 401:
                raise AuthError("Invalid Stability API key")
            if response.status_code == 429:
                raise RateLimitError("Stability rate limit exceeded")
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Stability network error: {e}")


class OpenAIProvider(BaseProvider):
    @property
    def is_configured(self) -> bool:
        return bool(_get_config("OPENAI_API_KEY"))

    def _generate(self, prompt: str) -> bytes:
        api_key = _get_config("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            if image_url:
                return requests.get(image_url, timeout=30).content
            raise ProviderError("OpenAI returned no image URL")
        except Exception as e:
            if "Authentication" in str(e) or "401" in str(e):
                raise AuthError(f"OpenAI authentication failed: {e}")
            if "RateLimit" in str(e) or "429" in str(e):
                raise RateLimitError(f"OpenAI rate limit exceeded: {e}")
            raise NetworkError(f"OpenAI generation failed: {e}")


class ProviderManager:
    def __init__(self):
        # Priority order
        self.providers: list[BaseProvider] = [
            FalProvider(),
            ReplicateProvider(),
            HuggingFaceProvider(),
            StabilityProvider(),
            OpenAIProvider(),
        ]

    def generate(
        self, prompt: str, status_callback: Callable[[str], None] | None = None
    ) -> tuple[bytes | None, str | None, str | None, float]:
        """
        Attempts to generate an image using configured providers in priority order.
        Returns: (image_bytes, provider_name_used, error_message, duration_seconds)
        """
        configured_providers = [p for p in self.providers if p.is_configured]

        if not configured_providers:
            return (
                None,
                None,
                "No image generation API keys found. Please configure a provider (e.g., HF_API_KEY).",
                0.0,
            )

        errors = []
        start_time = time.time()
        for provider in configured_providers:
            if status_callback:
                status_callback(provider.name)

            try:
                image_bytes = provider.generate_image(prompt)
                duration = time.time() - start_time
                return image_bytes, provider.name, None, duration
            except AuthError as e:
                errors.append(f"{provider.name}: Authentication Failed ({e})")
                continue
            except Exception as e:
                errors.append(f"{provider.name}: {str(e)}")
                continue

        duration = time.time() - start_time
        error_msg = "All configured providers failed.\n" + "\n".join(f"- {err}" for err in errors)
        return None, None, error_msg, duration


# Singleton instance
_manager = ProviderManager()


def generate_image(
    prompt: str, status_callback: Callable[[str], None] | None = None
) -> tuple[bytes | None, str | None, str | None, float]:
    return _manager.generate(prompt, status_callback)
