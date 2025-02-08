import streamlit as st
import pandas as pd
from datetime import datetime

from modules import (
    chronological_age,
    rounded_age,
    kg_to_lbs,
    cm_to_inches,
    get_height_coefficient,
    get_weight_coefficient,
    adjust_mother_height_inches,
    inches_to_cm,
    adjust_father_height_inches,
    calculate_midparent_height_cm,
    get_midparent_coefficient,
    calculate_midparent_inches,
    get_intersect,
    calculate_predicted_adult_height_cm,
    calculate_percent_predicted_height,
    calculate_biological_age,
    calculate_ba_ca,
    calculate_timing,
    calculate_alt_timing,
    calculate_maturity_status,
    calculate_lower_bound_50,
    calculate_upper_bound_50,
    calculate_lower_bound_90,
    calculate_upper_bound_90,
)

st.set_page_config(layout="wide")

############################################################################

# Load data
@st.cache_data
def load_all_data():
    errors_df = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Errors')
    sa_df = pd.read_excel('Maturation_calculator.xlsx', sheet_name='SA')
    metrics_df = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Metric coefficients')
    return errors_df, sa_df, metrics_df

errors_df, sa_df, metrics_df = load_all_data()

############################################################################

# Define LTAD brand colors
DARK_BLUE = "#0F1B34"
GREEN = "#23FF00"
WHITE = "#FFFFFF"

# Custom CSS for Styling
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {DARK_BLUE} !important;
            color: {WHITE} !important;
            font-family: Helvetica, sans-serif;
        }}
        .main-header {{
            font-size: 42px !important;
            color: {GREEN} !important;
            text-align: center;
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 24px;
            color: {GREEN};
            margin-bottom: 15px;
        }}
        .result-text {{
            font-size: 18px;
            margin-bottom: 10px;
        }}
        .stDownloadButton > button {{
            background-color: {GREEN} !important;
            color: {DARK_BLUE} !important;
            font-weight: bold;
            font-size: 16px;
            border-radius: 10px;
        }}
        .stDownloadButton > button:hover {{
            background-color: {WHITE} !important;
            color: {DARK_BLUE} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Page Title
st.markdown('<h1 class="main-header">Maturation Calculator</h1>', unsafe_allow_html=True)

# Sidebar inputs
st.sidebar.header('Input Parameters')

name = st.sidebar.text_input("Name")
gender = st.sidebar.selectbox('Gender', ['Male', 'Female'])
test_date = st.sidebar.date_input('Test Date', datetime.now().date())
dob = st.sidebar.date_input('Date of Birth', datetime.now().date() - pd.Timedelta(days=365 * 14))

body_mass_kg = st.sidebar.number_input('Body Mass (kg)', value=50.0, format="%.1f")
standing_height_cm = st.sidebar.number_input('Standing Height (cm)', value=160.0, format="%.1f")
mothers_height_cm = st.sidebar.number_input("Mother's Height (cm)", value=165.0, format="%.1f")
fathers_height_cm = st.sidebar.number_input("Father's Height (cm)", value=180.0, format="%.1f")

# Calculations
chronological_age_val = chronological_age(dob, test_date)
rounded_age_val = rounded_age(chronological_age_val)
height_coef = get_height_coefficient(gender, rounded_age_val)
weight_coef = get_weight_coefficient(gender, rounded_age_val)
mother_height_inches = cm_to_inches(mothers_height_cm)
father_height_inches = cm_to_inches(fathers_height_cm)
adj_mother_cm = inches_to_cm(adjust_mother_height_inches(mother_height_inches))
adj_father_cm = inches_to_cm(adjust_father_height_inches(father_height_inches))
midparent_height_cm = calculate_midparent_height_cm(adj_mother_cm, adj_father_cm)
midparent_coef = get_midparent_coefficient(gender, rounded_age_val)
intersect_val = get_intersect(gender, rounded_age_val)
predicted_height_cm = calculate_predicted_adult_height_cm(
    intersect_val, height_coef, standing_height_cm, weight_coef, body_mass_kg, midparent_coef, midparent_height_cm
)
percent_predicted_height = calculate_percent_predicted_height(standing_height_cm, predicted_height_cm)
biological_age_val = calculate_biological_age(gender, percent_predicted_height, sa_df)
ba_ca_val = calculate_ba_ca(chronological_age_val, biological_age_val)
timing_val = calculate_timing(ba_ca_val)
alt_timing_val = calculate_alt_timing(ba_ca_val)
maturity_status_val = calculate_maturity_status(percent_predicted_height)
lower_50 = calculate_lower_bound_50(predicted_height_cm, rounded_age_val)
upper_50 = calculate_upper_bound_50(predicted_height_cm, rounded_age_val)
lower_90 = calculate_lower_bound_90(predicted_height_cm, rounded_age_val)
upper_90 = calculate_upper_bound_90(predicted_height_cm, rounded_age_val)

# Results Display in Two Columns
col1, col2 = st.columns(2)

with col1:
    st.markdown('<h2 class="section-title">Age Calculations</h2>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Chronological Age: {chronological_age_val:.2f}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Biological Age: {biological_age_val:.2f}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">BA-CA: {ba_ca_val:.2f}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Rounded Age: {rounded_age_val:.1f}</p>', unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">Height Predictions</h2>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Predicted Adult Height: {predicted_height_cm:.1f} cm</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Percent of Adult Height: {percent_predicted_height:.1f}%</p>', unsafe_allow_html=True)

with col2:
    st.markdown('<h2 class="section-title">Maturity Assessment</h2>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Maturity Status: {maturity_status_val}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Timing: {timing_val}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Alt. Timing: {alt_timing_val}</p>', unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">Height Bounds</h2>', unsafe_allow_html=True)
    st.markdown('<h3>50% Confidence Interval</h3>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Lower: {lower_50:.1f} cm</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Upper: {upper_50:.1f} cm</p>', unsafe_allow_html=True)
    st.markdown('<h3>90% Confidence Interval</h3>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Lower: {lower_90:.1f} cm</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Upper: {upper_90:.1f} cm</p>', unsafe_allow_html=True)

# Download Button
results_dict = {
    'Name': name,
    'Gender': gender,
    'Test Date': test_date.strftime('%Y-%m-%d'),
    'Date of Birth': dob.strftime('%Y-%m-%d'),
    'Body Mass (kg)': body_mass_kg,
    'Standing Height (cm)': standing_height_cm,
    "Mother's Height (cm)": mothers_height_cm,
    "Father's Height (cm)": fathers_height_cm,
    'Chronological Age': chronological_age_val,
    'Biological Age': biological_age_val,
    'BA-CA': ba_ca_val,
    'Predicted Adult Height (cm)': predicted_height_cm,
    'Percent of Adult Height': percent_predicted_height,
    'Maturity Status': maturity_status_val,
    'Timing': timing_val,
    'Alt. Timing': alt_timing_val,
    '50% Lower Bound': lower_50,
    '50% Upper Bound': upper_50,
    '90% Lower Bound': lower_90,
    '90% Upper Bound': upper_90,
}
results_df = pd.DataFrame([results_dict])
csv = results_df.to_csv(index=False)

st.download_button(
    label="Download Results as CSV",
    data=csv,
    file_name="maturation_results.csv",
    mime="text/csv"
)
