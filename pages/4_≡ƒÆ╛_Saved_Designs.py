"""
Saved Designs page.
Shows every design the user has favorited from the Design Generator,
with the ability to download, unfavorite, or view the prompt used.
"""

from __future__ import annotations

import streamlit as st

from utils.helpers import init_session_state, toggle_favorite
from utils.theme import app_footer, configure_page, glass_card, section_header

configure_page("Saved Designs", "💾")
init_session_state()

section_header("Saved Designs", "Your favorited designs, all in one place")

favorites = st.session_state.favorites

if not favorites:
    glass_card(
        "<h4>💔 No favorites yet</h4>"
        "<p style='color:#b9b6cf;'>Generate a design and tap the ❤️ Favorite button to save it here.</p>"
    )
else:
    st.caption(f"{len(favorites)} saved design{'s' if len(favorites) != 1 else ''}")
    num_cols = 3
    cols = st.columns(num_cols)
    for idx, record in enumerate(favorites):
        with cols[idx % num_cols]:
            image_bytes = bytes.fromhex(record["image_bytes_hex"])
            st.image(image_bytes, use_container_width=True, caption=record["room_type"])
            st.caption(record["timestamp"])
            with st.expander("View prompt"):
                st.code(record["prompt"], language="markdown")
            b1, b2 = st.columns(2)
            b1.download_button(
                "⬇️ Download", data=image_bytes, file_name=f"design_{record['id']}.png",
                mime="image/png", use_container_width=True, key=f"dl_{record['id']}",
            )
            if b2.button("💔 Remove", use_container_width=True, key=f"rm_{record['id']}"):
                toggle_favorite(record)
                st.rerun()
            st.write("")

app_footer()
