"""
app.py
------
Main entry point for AI Interior Designer Pro.
Renders the Home page and sets up shared session state. Streamlit
automatically discovers additional pages inside the `pages/` folder and
shows them in the sidebar navigation.
"""

from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from utils.helpers import init_session_state
from utils.theme import app_footer, configure_page, glass_card, section_header

configure_page("Home", "🏛️")
init_session_state()

# ---------------------------------------------------------------------------
# Hero Section
# ---------------------------------------------------------------------------
st.markdown('<span class="tag-pill">✨ AI-POWERED INTERIOR DESIGN</span>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-title">Design Beautiful Spaces <span class="gradient-text">with AI</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="hero-subtitle">Describe your dream room — or pick from curated style options — and let '
    "AI Interior Designer Pro generate photorealistic, magazine-worthy interior visualizations in seconds.</p>",
    unsafe_allow_html=True,
)

col_a, col_b, _ = st.columns([1, 1, 3])
with col_a:
    if st.button("🎨 Start Designing", use_container_width=True):
        st.switch_page("pages/2_🎨_Design_Generator.py")
with col_b:
    if st.button("🖼️ Browse Gallery", use_container_width=True):
        st.switch_page("pages/3_🖼️_Gallery.py")

st.write("")
st.write("")

# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
stat_cols = st.columns(4)
stats = [
    ("19+", "Room Types"),
    ("14", "Design Themes"),
    ("100%", "Streamlit Cloud Ready"),
    ("∞", "Design Possibilities"),
]
for col, (number, label) in zip(stat_cols, stats):
    with col:
        glass_card(f'<div class="stat-number">{number}</div><div class="stat-label">{label}</div>')

st.write("")

# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------
section_header("Everything you need to design like a pro", "A complete AI design studio in your browser")

feature_cols = st.columns(3)
features = [
    ("🧠", "Smart Prompt Engineering", "Your room type, theme, materials, and lighting choices are "
     "automatically converted into an optimized, professional-grade AI prompt."),
    ("💬", "AI Design Assistant", "Chat with Aura, your on-demand interior designer, for furniture "
     "ideas, color palettes, Vastu &amp; Feng Shui tips, and budget planning."),
    ("🖼️", "Pinterest-Style Gallery", "Explore a curated, masonry-style gallery of design inspiration "
     "across every style and room type."),
    ("💾", "Save &amp; Revisit", "Favorite your best designs and revisit your full generation history "
     "any time — nothing is lost between sessions."),
    ("🔌", "Plug-and-Play Image Engine", "Modular image generation architecture — swap between Hugging Face, "
     "Stability AI, Replicate, or Fal.ai with a single config change."),
    ("🎛️", "Deep Customization", "Fine-tune room type, ceiling, flooring, wall material, décor, "
     "budget tier and more before every generation."),
]
for i, (icon, title, desc) in enumerate(features):
    with feature_cols[i % 3]:
        glass_card(f"<h4>{icon} {title}</h4><p style='color:#b9b6cf;'>{desc}</p>")

st.write("")

# ---------------------------------------------------------------------------
# Testimonials
# ---------------------------------------------------------------------------
section_header("Loved by design enthusiasts")

t_cols = st.columns(3)
testimonials = [
    ("\"I redesigned my entire living room concept in an afternoon. The prompt engineering "
     "is genuinely impressive.\"", "— Meera K., Homeowner"),
    ("\"As a student architect, the gallery and assistant have become my go-to inspiration "
     "tool.\"", "— Rohan D., Architecture Student"),
    ("\"Finally an interior AI tool that lets you control every material and lighting "
     "detail before generating.\"", "— Priya S., Interior Consultant"),
]
for col, (quote, author) in zip(t_cols, testimonials):
    with col:
        st.markdown(
            f'<div class="testimonial-card">{quote}<div class="testimonial-author">{author}</div></div>',
            unsafe_allow_html=True,
        )

app_footer()
