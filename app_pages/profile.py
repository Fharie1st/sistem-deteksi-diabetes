# =========================
# FILE: profile.py
# =========================

import streamlit as st
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image

from utils.database import get_profile, update_profile


DEFAULT_PHOTO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"


def uploaded_photo_to_base64(uploaded_photo):
    if uploaded_photo is None:
        return None

    # Buka gambar
    image = Image.open(uploaded_photo).convert("RGB")

    width, height = image.size

    # Crop tengah agar hasilnya kotak
    min_side = min(width, height)

    left = (width - min_side) // 2
    top = (height - min_side) // 2
    right = left + min_side
    bottom = top + min_side

    image = image.crop((left, top, right, bottom))

    # Resize agar gambar rapi dan ukuran tidak terlalu besar
    image = image.resize((500, 500))

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return f"data:image/png;base64,{encoded}"


def file_path_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(
            img_file.read()
        ).decode("utf-8")

    suffix = Path(image_path).suffix.lower().replace(".", "")

    if suffix == "jpg":
        suffix = "jpeg"

    return f"data:image/{suffix};base64,{encoded}"


def get_photo_source(photo_data):
    if photo_data and str(photo_data).startswith("data:image"):
        return photo_data

    # Untuk jaga-jaga kalau data lama masih berupa path profile_images/username.png
    if photo_data and Path(photo_data).exists():
        return file_path_to_base64(photo_data)

    return DEFAULT_PHOTO


def show_profile():

    if not st.session_state.logged_in:
        st.warning("Silakan login terlebih dahulu")
        st.stop()

    username = st.session_state.username

    profile = get_profile(username)

    profile_name = profile[1] if profile[1] else username
    profile_email = profile[2] if profile[2] else "Belum ada email"
    profile_mobile = profile[3] if profile[3] else ""
    profile_location = profile[4] if profile[4] else ""
    profile_photo_data = profile[5] if profile[5] else ""

    photo_src = get_photo_source(profile_photo_data)

    # =========================
    # STYLE
    # =========================

    st.markdown("""
    <style>
        .block-container {
            padding-top: 3rem;
        }

        .profile-header {
            max-width: 900px;
            margin: 0 auto 25px auto;
            padding-bottom: 25px;
            border-bottom: 1px solid #eeeeee;
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .profile-photo-circle {
            width: 175px;
            height: 175px;
            border-radius: 50%;
            object-fit: cover;
            object-position: center;
            border: 2px solid #eeeeee;
            display: block;
        }

        .profile-info {
            margin-left: 0px;
        }

        .profile-name {
            font-size: 36px;
            font-weight: 800;
            color: #111111;
            margin-bottom: 5px;
            line-height: 1.1;
        }

        .profile-email {
            font-size: 16px;
            color: #666666;
        }

        .profile-form-title {
            max-width: 900px;
            margin: 0 auto 10px auto;
            font-size: 20px;
            font-weight: 600;
        }

        .profile-label {
            font-size: 14px;
            font-weight: 600;
            color: #222222;
            padding-top: 12px;
        }

        div[data-testid="stTextInput"] input {
            background-color: #f0f2f6;
            border-radius: 8px;
            border: none;
        }

        div[data-testid="stFileUploader"] {
            background-color: #f0f2f6;
            padding: 12px;
            border-radius: 8px;
        }

        div[data-testid="stFormSubmitButton"] button {
            background-color: #1f8bff;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 18px;
            font-size: 14px;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            background-color: #0d6fd1;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    # =========================
    # HEADER PROFILE
    # =========================

    st.markdown(
        f"""
        <div class="profile-header">
            <img src="{photo_src}" class="profile-photo-circle">
            <div class="profile-info">
                <div class="profile-name">{profile_name}</div>
                <div class="profile-email">{profile_email}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # FORM PROFILE
    # =========================

    st.markdown(
        '<div class="profile-form-title">Informasi Profile</div>',
        unsafe_allow_html=True
    )

    with st.container(border=True):

        with st.form("profile_form"):

            col1, col2 = st.columns([1, 3])

            with col1:
                st.markdown(
                    '<div class="profile-label">Name</div>',
                    unsafe_allow_html=True
                )

            with col2:
                name = st.text_input(
                    "Name",
                    value=profile_name,
                    label_visibility="collapsed"
                )

            col3, col4 = st.columns([1, 3])

            with col3:
                st.markdown(
                    '<div class="profile-label">Email account</div>',
                    unsafe_allow_html=True
                )

            with col4:
                email = st.text_input(
                    "Email account",
                    value="" if profile_email == "Belum ada email" else profile_email,
                    placeholder="yourname@gmail.com",
                    label_visibility="collapsed"
                )

            col5, col6 = st.columns([1, 3])

            with col5:
                st.markdown(
                    '<div class="profile-label">Mobile number</div>',
                    unsafe_allow_html=True
                )

            with col6:
                mobile = st.text_input(
                    "Mobile number",
                    value=profile_mobile,
                    placeholder="Add number",
                    label_visibility="collapsed"
                )

            col7, col8 = st.columns([1, 3])

            with col7:
                st.markdown(
                    '<div class="profile-label">Location</div>',
                    unsafe_allow_html=True
                )

            with col8:
                location = st.text_input(
                    "Location",
                    value=profile_location,
                    placeholder="Indonesia",
                    label_visibility="collapsed"
                )

            col9, col10 = st.columns([1, 3])

            with col9:
                st.markdown(
                    '<div class="profile-label">Profile photo</div>',
                    unsafe_allow_html=True
                )

            with col10:
                uploaded_photo = st.file_uploader(
                    "Profile photo",
                    type=["jpg", "jpeg", "png"],
                    label_visibility="collapsed"
                )

            save_button = st.form_submit_button(
                "Save Change"
            )

    if save_button:

        new_photo_data = profile_photo_data

        if uploaded_photo is not None:
            new_photo_data = uploaded_photo_to_base64(
                uploaded_photo
            )

        update_profile(
            username=username,
            name=name,
            email=email,
            mobile=mobile,
            location=location,
            photo_path=new_photo_data
        )

        st.success("Profile berhasil disimpan.")

        st.rerun()