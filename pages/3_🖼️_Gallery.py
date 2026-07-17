"""
Gallery page.
Pinterest-style masonry gallery of curated design inspiration, generated
on the fly via the image service so it works out of the box, with
category filters and search.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from services import image_service
from utils.helpers import init_session_state
from utils.theme import app_footer, configure_page, section_header

configure_page("Gallery", "🖼️")
init_session_state()

section_header("Design Gallery", "Pinterest-style inspiration across every style")

PROMPTS_FILE = Path(__file__).resolve().parent.parent / "prompts" / "sample_prompts.json"
with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
    gallery_items = json.load(f)

categories = ["All"] + sorted({item["category"] for item in gallery_items})
c1, c2 = st.columns([1, 2])
selected_category = c1.selectbox("Category", categories)
search_query = c2.text_input("🔍 Search designs", placeholder="e.g. luxury, kitchen, boho...")

filtered = gallery_items
if selected_category != "All":
    filtered = [i for i in filtered if i["category"] == selected_category]
if search_query.strip():
    q = search_query.lower()
    filtered = [i for i in filtered if q in i["title"].lower() or q in i["prompt"].lower()]

st.caption(f"Showing {len(filtered)} of {len(gallery_items)} designs")

num_cols = 3
cols = st.columns(num_cols)

for idx, item in enumerate(filtered):
    with cols[idx % num_cols]:
        with st.spinner(f"Loading {item['title']}..."):
            image_bytes, _, err, _ = image_service.generate_image(item["prompt"])
        
        if err:
            st.error(err)
            continue
        st.image(image_bytes, use_container_width=True)
        st.markdown(f"**{item['title']}**")
        st.markdown(f'<span class="badge badge-purple">{item["category"]}</span>', unsafe_allow_html=True)
        with st.expander("View prompt"):
            st.code(item["prompt"], language="markdown")
        st.write("")

if not filtered:
    st.info("No designs match your search. Try a different category or keyword.")

app_footer()
