"""
theme.py
--------
Handles global Streamlit page configuration and injects the premium
glassmorphism CSS theme used across every page of the application.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

CSS_PATH = Path(__file__).resolve().parent.parent / "css" / "style.css"


def load_css() -> None:
    """Inject the shared stylesheet into the current Streamlit page."""
    if CSS_PATH.exists():
        css = CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def configure_page(title: str, icon: str = "🏛️") -> None:
    """
    Apply consistent page config + theme to every page in the app.

    Call this as the very first Streamlit command on each page.
    """
    st.set_page_config(
        page_title=f"{title} · AI Interior Designer Pro",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css()


def glass_card(content_html: str) -> None:
    """Render a block of HTML inside a styled glassmorphism card."""
    st.markdown(f'<div class="glass-card">{content_html}</div>', unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "") -> None:
    """Render a consistent gradient section header used across pages."""
    st.markdown(f'<h2 class="gradient-text">{title}</h2>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p style="color:#b9b6cf;margin-top:-10px;">{subtitle}</p>', unsafe_allow_html=True)


def app_footer() -> None:
    """Render the shared footer at the bottom of a page."""
    st.markdown(
        """
        <div class="app-footer">
            Built with ❤️ using Streamlit &amp; Groq · <span class="badge badge-purple">AI Interior Designer Pro</span>
            · v1.0.0
        </div>
        """,
        unsafe_allow_html=True,
    )
