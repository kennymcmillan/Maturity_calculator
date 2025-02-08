import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from modules import *

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

# Streamlit UI

# Define LTAD brand colors
DARK_BLUE = "#0F1B34"
GREEN = "#23FF00"
WHITE = "#FFFFFF"
GREY = "#9F9F9F"

# Custom CSS for styling
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {DARK_BLUE} !important;
            color: {WHITE} !important;
        }}
        .main-header {{
            font-size: 42px !important;
            color: {GREEN} !important;
            text-align: center;
            font-family: Helvetica, sans-serif;
        }}
        .sub-header {{
            font-size: 24px !important;
            color: {GREEN};
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
            background-color: {WHITE} !important;
            color: {DARK_BLUE} !important;
        }}
        .stMarkdown p, .stMarkdown div {{
            color: {WHITE} !important;
            text-align: center;
            font-family: Helvetica, sans-serif;
            font-size: 18px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Page Title
st.markdown('<h1 class="main-header">Maturation Calculator</h1>', unsafe_allow_html=True)

#st.title('Maturation Calculator')

# Sidebar inputs
st.sidebar.header('Input Parameters')

name = st.sidebar.text_input("Name")
gender = st.sidebar.selectbox('Gender', ['Male', 'Female'])
test_date = st.sidebar.date_input('Test Date', datetime.now().date())
dob = st.sidebar.date_input('Date of Birth', datetime.now().date() - pd.Timedelta(days=365*14))

body_mass_kg = st.sidebar.number_input('Body Mass (kg)', value=50.0, format="%.1f")
standing_height_cm = st.sidebar.number_input('Standing Height (cm)', value=160.0, format="%.1f")
mothers_height_cm = st.sidebar.number_input("Mother's Height (cm)", value=165.0, format="%.1f")
fathers_height_cm = st.sidebar.number_input("Father's Height (cm)", value=180.0, format="%.1f")

# Validate input before performing calculations
if dob and test_date:
    chronological_age_val = (test_date - dob).days / 365.25
else:
    chronological_age_val = None

chronological_age_val = chronological_age(dob, test_date)
rounded_age_val = rounded_age(chronological_age_val)
weight_lbs = kg_to_lbs(body_mass_kg)
height_inches = cm_to_inches(standing_height_cm)

height_coef = get_height_coefficient(gender, rounded_age_val)
weight_coef = get_weight_coefficient(gender, rounded_age_val)

mother_height_inches = cm_to_inches(mothers_height_cm)
father_height_inches = cm_to_inches(fathers_height_cm)

adj_mother_inches = adjust_mother_height_inches(mother_height_inches)
adj_father_inches = adjust_father_height_inches(father_height_inches)

adj_mother_cm = inches_to_cm(adj_mother_inches)
adj_father_cm = inches_to_cm(adj_father_inches)

midparent_height_cm = calculate_midparent_height_cm(adj_mother_cm, adj_father_cm)
midparent_coef = get_midparent_coefficient(gender, rounded_age_val)
midparent_inches = calculate_midparent_inches(gender, midparent_height_cm)

intersect_val = get_intersect(gender, rounded_age_val)
predicted_height_cm = calculate_predicted_adult_height_cm(intersect_val, height_coef, standing_height_cm, weight_coef, body_mass_kg, midparent_coef, midparent_height_cm)

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

# Display results
st.header('Results')

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('Age Calculations')
    st.write(f'Chronological Age: {chronological_age_val:.2f}')
    st.write(f'Biological Age: {biological_age_val:.2f}')
    st.write(f'BA-CA: {ba_ca_val:.2f}')
    st.write(f'Rounded Age: {rounded_age_val:.1f}')

with col2:
    st.subheader('Height Predictions')
    st.write(f'Predicted Adult Height: {predicted_height_cm:.1f} cm')
    st.write(f'Percent of Adult Height: {percent_predicted_height:.1f}%')

with col3:
    st.subheader('Maturity Assessment')
    st.write(f'Maturity Status: {maturity_status_val}')
    st.write(f'Timing: {timing_val}')
    st.write(f'Alt. Timing: {alt_timing_val}')

st.header('Height Bounds')

col1, col2 = st.columns(2)

with col1:
    st.subheader('50% Confidence Interval')
    st.write(f"Lower: {lower_50:.1f} cm")
    st.write(f"Upper: {upper_50:.1f} cm")

with col2:
    st.subheader('90% Confidence Interval')
    st.write(f"Lower: {lower_90:.1f} cm")
    st.write(f"Upper: {upper_90:.1f} cm")

# Download button
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
    '90% Upper Bound': upper_90
}

results_df = pd.DataFrame([results_dict])
csv = results_df.to_csv(index=False)

st.download_button(
    label="Download Results as CSV",
    data=csv,
    file_name="maturation_results.csv",
    mime="text/csv"
)
