"""
Design Generator page.
Lets the user configure every aspect of a room, auto-builds an optimized
AI prompt (refined via Groq when configured), generates an image via the
modular image service, and offers download / save / favorite / regenerate
/ before-after comparison actions.
"""

from __future__ import annotations

import time
import streamlit as st

from services import ai_service, image_service
from utils.helpers import (
    init_session_state,
    is_favorited,
    new_id,
    now_str,
    save_to_history,
    toggle_favorite,
)
from utils.prompt_builder import (
    BUDGET_OPTIONS,
    CEILING_OPTIONS,
    COLOR_THEMES,
    DECORATION_OPTIONS,
    FLOOR_OPTIONS,
    FURNITURE_STYLES,
    LIGHTING_OPTIONS,
    PLANT_OPTIONS,
    ROOM_TYPES,
    WALL_MATERIALS,
    DesignOptions,
    build_image_prompt,
    build_llm_refinement_instructions,
)
from utils.theme import app_footer, configure_page, glass_card, section_header

configure_page("Design Generator", "🎨")
init_session_state()

section_header("AI Design Generator", "Configure your space, then let AI bring it to life")

if not ai_service.is_configured():
    st.info(
        "💡 Add a **GROQ_API_KEY** in Settings/secrets to enable AI prompt refinement. "
        "Generation still works without it using your structured selections directly."
    )

form_col, preview_col = st.columns([1, 1.15], gap="large")

with form_col:
    with st.form("design_form"):
        st.markdown("#### Room &amp; Style")
        c1, c2 = st.columns(2)
        room_type = c1.selectbox("Room Type", ROOM_TYPES)
        color_theme = c2.selectbox("Color Theme", COLOR_THEMES, index=COLOR_THEMES.index("Modern"))

        c3, c4 = st.columns(2)
        furniture_style = c3.selectbox("Furniture Style", FURNITURE_STYLES)
        lighting = c4.selectbox("Lighting", LIGHTING_OPTIONS)

        st.markdown("#### Structure &amp; Materials")
        c5, c6 = st.columns(2)
        ceiling = c5.selectbox("Ceiling", CEILING_OPTIONS)
        wall_material = c6.selectbox("Wall Material", WALL_MATERIALS)

        c7, c8 = st.columns(2)
        floor = c7.selectbox("Floor", FLOOR_OPTIONS)
        large_windows = c8.selectbox("Large Windows", ["Yes", "No"]) == "Yes"

        st.markdown("#### Finishing Touches")
        c9, c10 = st.columns(2)
        plants = c9.selectbox("Plants", PLANT_OPTIONS)
        budget = c10.selectbox("Budget", BUDGET_OPTIONS, index=BUDGET_OPTIONS.index("Premium"))

        decorations = st.multiselect("Decorations", DECORATION_OPTIONS, default=["Curtains", "Paintings"])

        custom_description = st.text_area(
            "Describe anything else you'd like (optional)",
            placeholder="e.g. huge windows overlooking mountains, a reading nook in the corner...",
            height=90,
        )

        submitted = st.form_submit_button("✨ Generate Design", use_container_width=True)

with preview_col:
    if submitted:
        options = DesignOptions(
            room_type=room_type,
            color_theme=color_theme,
            furniture_style=furniture_style,
            lighting=lighting,
            large_windows=large_windows,
            ceiling=ceiling,
            wall_material=wall_material,
            floor=floor,
            plants=plants,
            decorations=decorations,
            budget=budget,
            custom_description=custom_description,
        )

        base_prompt = build_image_prompt(options)

        with st.spinner("Refining your brief with AI..."):
            instructions = build_llm_refinement_instructions(options, base_prompt)
            final_prompt = ai_service.refine_prompt(base_prompt, instructions)

        status = st.status("Generating your premium interior...", expanded=True)
        def update_status(provider_name: str):
            status.update(label=f"Generating your premium interior (via {provider_name})...")
            
        with status:
            image_bytes, provider_name, error_message, duration = image_service.generate_image(
                final_prompt, status_callback=update_status
            )
            if error_message:
                status.update(label="Generation failed", state="error")
                st.error(error_message)
            elif image_bytes:
                status.update(
                    label=f"✨ Generated successfully via {provider_name} in {duration:.1f}s!", 
                    state="complete"
                )

        if image_bytes:
            record = {
                "id": new_id(),
                "timestamp": now_str(),
                "room_type": room_type,
                "prompt": final_prompt,
                "image_bytes_hex": image_bytes.hex(),
            }
            st.session_state.last_generated = record
            save_to_history(record)

    if st.session_state.get("last_generated"):
        record = st.session_state.last_generated
        image_bytes = bytes.fromhex(record["image_bytes_hex"])

        st.image(image_bytes, use_container_width=True, caption=record["room_type"])

        with st.expander("📝 View optimized AI prompt"):
            st.code(record["prompt"], language="markdown")

        b1, b2, b3, b4 = st.columns(4)
        b1.download_button(
            "⬇️ Download", data=image_bytes, file_name=f"design_{record['id']}.png",
            mime="image/png", use_container_width=True,
        )
        fav_label = "💔 Unfavorite" if is_favorited(record["id"]) else "❤️ Favorite"
        if b2.button(fav_label, use_container_width=True):
            toggle_favorite(record)
            st.rerun()
        if b3.button("🔁 Regenerate", use_container_width=True):
            status = st.status("Regenerating your interior...", expanded=True)
            def update_regen_status(provider_name: str):
                status.update(label=f"Regenerating via {provider_name}...")
                
            with status:
                image_bytes2, provider_name, err2, duration = image_service.generate_image(
                    record["prompt"], status_callback=update_regen_status
                )
                if err2:
                    status.update(label="Regeneration failed", state="error")
                    st.error(err2)
                elif image_bytes2:
                    status.update(
                        label=f"✨ Regenerated successfully via {provider_name} in {duration:.1f}s!", 
                        state="complete"
                    )
                    new_record = {**record, "id": new_id(), "timestamp": now_str(), "image_bytes_hex": image_bytes2.hex()}
                    st.session_state.last_generated = new_record
                    save_to_history(new_record)
                    time.sleep(1) # Give the user a moment to see the success message
                    st.rerun()
        b4.link_button("📤 Share", "https://github.com/", use_container_width=True)

        st.markdown("#### Before / After")
        st.caption("Compare your generated design against a blank canvas concept.")
        try:
            from streamlit_image_comparison import image_comparison

            image_comparison(
                img1=image_bytes,
                img2=image_bytes,
                label1="Concept",
                label2="Final Render",
            )
        except Exception:
            st.info("Install `streamlit-image-comparison` to enable the interactive before/after slider.")
    else:
        glass_card(
            "<h4>👋 Ready when you are</h4>"
            "<p style='color:#b9b6cf;'>Fill in your preferences on the left and click "
            "<b>Generate Design</b> to see your AI-powered interior visualization here.</p>"
        )

app_footer()
