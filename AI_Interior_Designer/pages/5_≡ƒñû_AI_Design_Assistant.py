"""
AI Design Assistant page.
Conversational chatbot ("Aura") powered by Groq, answering interior
design, furniture, color, lighting, budget, renovation, Vastu, Feng
Shui, space optimization, and storage questions.
"""

from __future__ import annotations

import streamlit as st

from services import ai_service
from utils.helpers import init_session_state
from utils.theme import app_footer, configure_page, section_header

configure_page("AI Design Assistant", "🤖")
init_session_state()

section_header("AI Design Assistant", "Chat with Aura, your on-demand interior designer")

SUGGESTED_PROMPTS = [
    "What color palette suits a small, dark living room?",
    "How should I light a home office for video calls?",
    "Suggest a budget-friendly bedroom makeover plan.",
    "What are the Vastu guidelines for a kitchen?",
    "How can I maximize storage in a small apartment?",
]

chip_cols = st.columns(len(SUGGESTED_PROMPTS))
clicked_prompt = None
for col, prompt_text in zip(chip_cols, SUGGESTED_PROMPTS):
    if col.button(prompt_text, use_container_width=True):
        clicked_prompt = prompt_text

st.write("")

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask Aura about furniture, colors, lighting, budget, Vastu, Feng Shui...")

final_input = user_input or clicked_prompt

if final_input:
    st.session_state.chat_messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    with st.chat_message("assistant"):
        with st.spinner("Aura is thinking..."):
            reply = ai_service.chat_with_assistant(st.session_state.chat_messages)
        st.markdown(reply)

    st.session_state.chat_messages.append({"role": "assistant", "content": reply})

if st.session_state.chat_messages and st.button("🗑️ Clear conversation"):
    st.session_state.chat_messages = []
    st.rerun()

app_footer()
