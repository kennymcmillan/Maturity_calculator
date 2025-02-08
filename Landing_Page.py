import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import base64

# Set the page configuration
st.set_page_config(page_title="Maturation Calculator", layout="wide", initial_sidebar_state="expanded")

# Define LTAD brand colors
DARK_BLUE = "#0F1B34"
GREEN = "#23FF00"
WHITE = "#FFFFFF"
GREY = "#9F9F9F"

# Helper function to set background from a local file
def set_background(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
            .stApp {{
                background: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)), url(data:image/png;base64,{encoded}) no-repeat center center fixed;
                background-size: cover;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set the background image with a lighter fade effect
set_background("background_2.png")

# Function to load and display logo in sidebar
def add_sidebar_logo(logo_file):
    with open(logo_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.sidebar.markdown(
        f"""
        <div style="text-align: center; padding-bottom: 20px;">
            <img src="data:image/png;base64,{encoded}" width="200">
        </div>
        """,
        unsafe_allow_html=True
    )

# Add grey logo to sidebar
add_sidebar_logo("logo_grey.png")

# Custom CSS for styling
st.markdown(
    f"""
    <style>
        .main-header {{
            font-size: 42px !important;
            color: {DARK_BLUE} !important;
            text-align: center;
            font-family: Helvetica, sans-serif;
        }}
        .sub-header {{
            font-size: 24px !important;
            color: {DARK_BLUE};
            text-align: center;
            font-family: Helvetica, sans-serif;
        }}
        .stButton > button {{
            background-color: {GREEN} !important;
            color: {DARK_BLUE} !important;
            font-weight: bold;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 5px;
        }}
        .stButton > button:hover {{
            background-color: {DARK_BLUE} !important;
            color: {GREEN} !important;
        }}
        .stMarkdown p {{
            color: {DARK_BLUE};
            text-align: center;
            font-family: Helvetica, sans-serif;
            font-size: 18px;
        }}
        .features {{
            color: {DARK_BLUE};
            text-align: center;
            font-family: Helvetica, sans-serif;
            font-size: 20px;
            font-weight: bold;
        }}
        .centered-button-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 30px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Landing Page Header
st.markdown('<h1 class="main-header">Welcome to the Maturation Calculator</h1>', unsafe_allow_html=True)

st.markdown('<p class="sub-header">Developed for Long Term Athletic Development (LTAD)</p>', unsafe_allow_html=True)

# Introductory Section
st.markdown(
    """
    <p style="text-align: center;">
        This tool is designed to assess the biological maturation of young athletes.<br>
        Using scientific models, it provides estimates of predicted adult height,<br>
        maturity timing, and biological age.
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="features">Key Features:</div>', unsafe_allow_html=True)

features = [
    "Predict adult height based on growth metrics",
    "Estimate biological age vs. chronological age",
    "Assess maturity timing (early, on-time, or late)",
    "Identify maturity status",
    "Provide confidence intervals for growth predictions",
]

for feature in features:
    st.markdown(f"<p class=\"features\">- {feature}</p>", unsafe_allow_html=True)

# # Centered button
# st.markdown('<div class="centered-button-container">', unsafe_allow_html=True)
# if st.button("Go to Calculator"):
#     st.markdown("<script>document.querySelector('.stButton button').parentElement.style.justifyContent = 'center';</script>", unsafe_allow_html=True)
#     st.switch_page("app.py")  # Assuming calculator.py is the main app file
# st.markdown('</div>', unsafe_allow_html=True)
