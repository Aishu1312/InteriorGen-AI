"""About page — project info, tech stack, and roadmap."""

from __future__ import annotations

import streamlit as st

from utils.helpers import init_session_state
from utils.theme import app_footer, configure_page, glass_card, section_header

configure_page("About", "ℹ️")
init_session_state()

section_header("About AI Interior Designer Pro", "Design Beautiful Spaces with AI")

glass_card(
    "<p style='color:#e5e2fa;'>AI Interior Designer Pro turns natural-language descriptions and "
    "structured style preferences into photorealistic interior visualizations, backed by an AI "
    "prompt-engineering pipeline and a conversational design assistant.</p>"
)

col1, col2 = st.columns(2)
with col1:
    glass_card(
        "<h4>🧩 Tech Stack</h4>"
        "<ul style='color:#b9b6cf;'>"
        "<li>Streamlit (frontend + app framework)</li>"
        "<li>Groq API — Llama 3.3 70B / Kimi K2 (LLM)</li>"
        "<li>Modular image generation service (Hugging Face / Stability / Replicate / Fal.ai)</li>"
        "<li>Custom CSS glassmorphism design system</li>"
        "</ul>"
    )
with col2:
    glass_card(
        "<h4>🗺️ Roadmap</h4>"
        "<ul style='color:#b9b6cf;'>"
        "<li>3D walkthrough previews</li>"
        "<li>Multi-image room-by-room design boards</li>"
        "<li>Shareable public design links</li>"
        "<li>Team/collaborative design workspaces</li>"
        "</ul>"
    )

section_header("Open Source")
glass_card(
    "<p style='color:#b9b6cf;'>This project is open source under the MIT License. Contributions are "
    "welcome — see <code>CONTRIBUTING.md</code> in the repository for guidelines on setting up your "
    "environment, coding standards, and submitting pull requests.</p>"
)

app_footer()
