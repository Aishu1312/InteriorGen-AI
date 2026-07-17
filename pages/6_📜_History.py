"""
History page.
Displays every design generated in this session (or persisted between
runs via data/history.json), newest first, with search/filter.
"""

from __future__ import annotations

import streamlit as st

from utils.helpers import init_session_state, is_favorited, toggle_favorite
from utils.theme import app_footer, configure_page, glass_card, section_header

configure_page("History", "📜")
init_session_state()

section_header("Generation History", "Every design you've created, newest first")

history = st.session_state.history

if not history:
    glass_card(
        "<h4>🕓 Nothing generated yet</h4>"
        "<p style='color:#b9b6cf;'>Head to the Design Generator to create your first design.</p>"
    )
else:
    search = st.text_input("🔍 Filter by room type or prompt keyword")
    filtered = history
    if search.strip():
        q = search.lower()
        filtered = [h for h in history if q in h["room_type"].lower() or q in h["prompt"].lower()]

    st.caption(f"{len(filtered)} of {len(history)} designs")

    for record in filtered:
        with st.container():
            col_img, col_meta = st.columns([1, 2])
            image_bytes = bytes.fromhex(record["image_bytes_hex"])
            col_img.image(image_bytes, use_container_width=True)
            with col_meta:
                st.markdown(f"**{record['room_type']}** · {record['timestamp']}")
                st.caption(record["prompt"][:220] + ("..." if len(record["prompt"]) > 220 else ""))
                bcol1, bcol2, bcol3 = st.columns(3)
                bcol1.download_button(
                    "⬇️ Download", data=image_bytes, file_name=f"design_{record['id']}.png",
                    mime="image/png", key=f"hist_dl_{record['id']}",
                )
                fav_label = "💔" if is_favorited(record["id"]) else "❤️"
                if bcol2.button(fav_label, key=f"hist_fav_{record['id']}"):
                    toggle_favorite(record)
                    st.rerun()
            st.divider()

app_footer()
