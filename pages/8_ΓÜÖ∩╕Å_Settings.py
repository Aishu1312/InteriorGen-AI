"""
Settings page.
Controls app-wide preferences: theme mode, accent color, animations,
language, font size, performance mode, and image quality. Also surfaces
configuration status for the Groq and image generation providers.
"""

from __future__ import annotations

import streamlit as st

from services import ai_service, image_service
from utils.helpers import init_session_state
from utils.theme import app_footer, configure_page, glass_card, section_header

configure_page("Settings", "⚙️")
init_session_state()

section_header("Settings", "Personalize your AI Interior Designer Pro experience")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Appearance")
    st.session_state.dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
    st.session_state.accent_color = st.color_picker("Accent Color", value=st.session_state.accent_color)
    st.session_state.animations_enabled = st.toggle(
        "Enable Animations", value=st.session_state.animations_enabled
    )
    st.session_state.font_size = st.select_slider(
        "Font Size", options=["Small", "Medium", "Large"], value=st.session_state.font_size
    )

with col2:
    st.markdown("#### Behavior")
    st.session_state.language = st.selectbox(
        "Language", ["English", "Hindi", "Spanish", "French", "German"],
        index=["English", "Hindi", "Spanish", "French", "German"].index(st.session_state.language),
    )
    st.session_state.performance_mode = st.toggle(
        "Performance Mode (reduces effects for low-end devices)",
        value=st.session_state.performance_mode,
    )
    st.session_state.image_quality = st.select_slider(
        "Image Quality", options=["Draft", "Standard", "High", "Ultra"],
        value=st.session_state.image_quality,
    )

st.write("")
section_header("Integration Status")

status_col1, status_col2 = st.columns(2)
with status_col1:
    groq_status = "✅ Connected" if ai_service.is_configured() else "⚠️ Not configured"
    glass_card(
        f"<h4>🧠 Groq LLM</h4><p style='color:#b9b6cf;'>Status: {groq_status}</p>"
        "<p style='color:#b9b6cf;font-size:0.85rem;'>Set <code>GROQ_API_KEY</code> in "
        "<code>.streamlit/secrets.toml</code> to enable prompt refinement and the AI Design Assistant.</p>"
    )
with status_col2:
    provider = image_service.get_provider_name()
    glass_card(
        f"<h4>🖼️ Image Provider</h4><p style='color:#b9b6cf;'>Active provider: <b>{provider}</b></p>"
        "<p style='color:#b9b6cf;font-size:0.85rem;'>Change <code>IMAGE_PROVIDER</code> "
        "(demo / huggingface / stability / replicate / fal) to switch backends with zero code changes.</p>"
    )

st.write("")
if st.button("💾 Save Preferences", use_container_width=False):
    st.success("Preferences saved for this session.")

app_footer()
