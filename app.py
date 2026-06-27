# app.py — VisioForge Streamlit frontend.
# This file contains ONLY UI rendering and user interaction handling.
# All business logic is delegated to api_client, prompt_templates, and utils.

import os
import time

import streamlit as st
from dotenv import load_dotenv

# Load .env for local development (no-op if already set or file absent)
load_dotenv()

from api_client import generate_image, validate_token
from config import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_TAGLINE,
    DEFAULT_SIZE,
    DEFAULT_STYLE,
    GALLERY_COLUMNS,
    IMAGE_SIZES,
    PRIMARY_MODEL,
)
from prompt_templates import (
    build_styled_prompt,
    get_style_info,
    get_style_negative_hints,
    list_styles,
)
from utils import (
    add_to_history,
    build_download_filename,
    build_remix_prompt,
    clear_history,
    format_timestamp,
    get_history,
    get_last_image,
    get_last_metadata,
    get_random_prompt,
    image_to_base64,
    init_session_state,
    truncate,
)


# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title=f"{APP_NAME} — AI Image Studio",
    page_icon="assets/logo.png" if os.path.exists("assets/logo.png") else "🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# CSS Injection
# ---------------------------------------------------------------------------

def _inject_css() -> None:
    css_path = "styles.css"
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


_inject_css()


# ---------------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------------

init_session_state()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(f"## {APP_NAME}")
    st.markdown(f"*{APP_TAGLINE}*")
    st.divider()

    # --- Generation Settings ---
    st.markdown("### Generation Settings")

    selected_size = st.selectbox(
        "Image Size",
        options=list(IMAGE_SIZES.keys()),
        index=list(IMAGE_SIZES.keys()).index(DEFAULT_SIZE),
        help="Output image dimensions. Larger sizes may take longer.",
    )

    st.markdown("### Advanced Options")

    with st.expander("Negative Prompt", expanded=False):
        st.caption(
            "Describe elements you want the model to exclude from the image."
        )
        negative_prompt_input = st.text_area(
            "Negative prompt",
            key="negative_prompt_area",
            placeholder="e.g. blurry, low quality, watermark, text, overexposed",
            height=80,
            label_visibility="collapsed",
        )

    st.divider()

    # --- Gallery Controls ---
    st.markdown("### Gallery")
    history = get_history()
    count = len(history)
    st.caption(f"{count} image{'s' if count != 1 else ''} generated this session.")

    if count > 0:
        if st.button("Clear History", type="secondary", use_container_width=True):
            clear_history()
            st.rerun()

    st.divider()

    # --- About ---
    with st.expander("About", expanded=False):
        st.markdown(
            f"""
            **{APP_NAME}** is a professional AI image studio built with
            Streamlit and the Hugging Face Inference API.

            **Model:** `{PRIMARY_MODEL}`

            **Version:** 1.0.0
            """
        )
        token_valid, token_error = validate_token()
        if token_valid:
            st.success("API token configured.")
        else:
            st.error("API token missing. See .env.example.")


# ---------------------------------------------------------------------------
# Main Header
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div class="vf-header">
        <h1 class="vf-title">{APP_NAME}</h1>
        <p class="vf-tagline">{APP_TAGLINE}</p>
        <p class="vf-description">{APP_DESCRIPTION}</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Main Two-Column Layout
# ---------------------------------------------------------------------------

left_col, right_col = st.columns([1, 1.2], gap="large")


# ---- LEFT PANEL: Controls ------------------------------------------------

with left_col:
    st.markdown('<div class="vf-panel">', unsafe_allow_html=True)
    st.markdown("#### Describe your image")

    # Prompt input.
    # value= is fed from "prompt_value" (a plain session state key, not a widget key)
    # so the Random Prompt button can write to it freely without triggering Streamlit's
    # "cannot modify widget key after instantiation" error.
    user_prompt = st.text_area(
        "Image prompt",
        value=st.session_state["prompt_value"],
        placeholder="A futuristic Indian city at night, glowing skyline over the Ganges...",
        height=120,
        max_chars=500,
        label_visibility="collapsed",
    )
    st.session_state["prompt_value"] = user_prompt

    if st.button("Random Prompt", type="secondary", use_container_width=False):
        st.session_state["prompt_value"] = get_random_prompt()
        st.rerun()


    st.markdown("#### Visual Style")

    # Style selection
    selected_style = st.radio(
        "Style",
        options=list_styles(),
        index=list_styles().index(DEFAULT_STYLE),
        key="style_radio",
        label_visibility="collapsed",
        horizontal=False,
    )

    # Style preview
    if selected_style:
        style_info = get_style_info(selected_style)
        keywords_str = "  ·  ".join(style_info.get("keywords", []))
        st.markdown(
            f"""
            <div class="vf-style-preview">
                <span class="vf-style-desc">{style_info.get('description', '')}</span>
                <br/>
                <span class="vf-style-keywords">{keywords_str}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    # Generate button
    generate_clicked = st.button(
        "Generate Image",
        type="primary",
        use_container_width=True,
        disabled=not bool(user_prompt and user_prompt.strip()),
    )

    st.markdown('</div>', unsafe_allow_html=True)


# ---- RIGHT PANEL: Image Output -------------------------------------------

with right_col:
    st.markdown('<div class="vf-panel">', unsafe_allow_html=True)

    last_image = get_last_image()
    last_meta = get_last_metadata()

    if generate_clicked and user_prompt and user_prompt.strip():
        # Resolve size
        width, height = IMAGE_SIZES[selected_size]

        # Resolve negative prompt — merge style hints with user input
        style_hints = get_style_negative_hints(selected_style)
        user_neg = negative_prompt_input.strip() if negative_prompt_input else ""
        combined_negative = ", ".join(filter(None, [user_neg, style_hints])) or None

        # Build the styled prompt
        final_prompt = build_styled_prompt(user_prompt, selected_style)

        # Generation with loading state
        with st.spinner("Generating your image…"):
            try:
                image_bytes = generate_image(
                    prompt=final_prompt,
                    negative_prompt=combined_negative,
                    width=width,
                    height=height,
                )
                record = add_to_history(
                    prompt=user_prompt,
                    style=selected_style,
                    final_prompt=final_prompt,
                    image_bytes=image_bytes,
                    image_size=selected_size,
                )
                last_image = image_bytes
                last_meta = record
                st.toast("Image generated successfully.")
            except ValueError as e:
                st.error(f"Configuration error: {e}")
                last_image = None
                last_meta = None
            except RuntimeError as e:
                st.error(
                    f"Generation failed. This may be due to API quota limits or a cold-start delay. "
                    f"Please wait a moment and try again.\n\n{e}"
                )
                last_image = None
                last_meta = None
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                last_image = None
                last_meta = None

    # --- Display Result ---
    if last_image:
        st.markdown("#### Generated Image")
        b64 = image_to_base64(last_image)
        st.markdown(
            f'<div class="vf-image-container"><img src="data:image/png;base64,{b64}" class="vf-generated-image" /></div>',
            unsafe_allow_html=True,
        )

        if last_meta:
            # Download button
            filename = build_download_filename(last_meta["prompt"], last_meta["style"])
            st.download_button(
                label="Download Image",
                data=last_image,
                file_name=filename,
                mime="image/png",
                use_container_width=True,
            )

            # Metadata card
            with st.expander("Generation Details", expanded=False):
                st.markdown(
                    f"""
                    <div class="vf-meta-card">
                        <div class="vf-meta-row"><span class="vf-meta-label">Prompt</span><span class="vf-meta-value">{last_meta['prompt']}</span></div>
                        <div class="vf-meta-row"><span class="vf-meta-label">Style</span><span class="vf-meta-value">{last_meta['style']}</span></div>
                        <div class="vf-meta-row"><span class="vf-meta-label">Size</span><span class="vf-meta-value">{last_meta['image_size']}</span></div>
                        <div class="vf-meta-row"><span class="vf-meta-label">Generated</span><span class="vf-meta-value">{format_timestamp(last_meta['timestamp'])}</span></div>
                        <div class="vf-meta-row"><span class="vf-meta-label">Full Prompt</span><span class="vf-meta-value vf-meta-prompt">{last_meta['final_prompt']}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Remix button
            st.markdown("---")
            st.markdown("**Remix this image with a different style**")
            remix_styles = [s for s in list_styles() if s != last_meta["style"]]
            remix_col1, remix_col2 = st.columns([2, 1])
            with remix_col1:
                remix_style = st.selectbox(
                    "Remix style",
                    options=remix_styles,
                    label_visibility="collapsed",
                )
            with remix_col2:
                remix_clicked = st.button("Remix", type="secondary", use_container_width=True)

            if remix_clicked and last_meta:
                remixed_prompt = build_remix_prompt(last_meta["prompt"], remix_style)
                final_remix_prompt = build_styled_prompt(remixed_prompt, remix_style)
                width, height = IMAGE_SIZES[selected_size]
                with st.spinner("Remixing…"):
                    try:
                        remix_bytes = generate_image(
                            prompt=final_remix_prompt,
                            width=width,
                            height=height,
                        )
                        add_to_history(
                            prompt=remixed_prompt,
                            style=remix_style,
                            final_prompt=final_remix_prompt,
                            image_bytes=remix_bytes,
                            image_size=selected_size,
                        )
                        st.toast("Remix complete.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Remix failed: {e}")

    else:
        # Empty state
        st.markdown(
            """
            <div class="vf-empty-state">
                <div class="vf-empty-icon">◈</div>
                <p class="vf-empty-title">Your canvas awaits</p>
                <p class="vf-empty-subtitle">Enter a prompt on the left and click Generate to create your first image.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Gallery Section
# ---------------------------------------------------------------------------

history = get_history()

if len(history) > 1:
    st.divider()
    st.markdown("### Gallery")
    st.caption(f"Your {len(history)} generated images from this session.")

    cols = st.columns(GALLERY_COLUMNS)
    for idx, record in enumerate(history):
        col = cols[idx % GALLERY_COLUMNS]
        with col:
            b64 = image_to_base64(record["image_bytes"])
            st.markdown(
                f'<div class="vf-gallery-card"><img src="data:image/png;base64,{b64}" class="vf-gallery-thumb" /></div>',
                unsafe_allow_html=True,
            )
            st.caption(f"**{record['style']}** · {truncate(record['prompt'], 45)}")
            st.caption(format_timestamp(record["timestamp"]))
            dl_name = build_download_filename(record["prompt"], record["style"])
            st.download_button(
                label="Download",
                data=record["image_bytes"],
                file_name=dl_name,
                mime="image/png",
                key=f"dl_{record['id']}",
                use_container_width=True,
            )
