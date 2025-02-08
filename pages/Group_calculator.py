# First create a complete version of the code

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

def validate_and_fix_dates(df):
    """Validate and fix dates in the dataframe to ensure test_date > date_of_birth"""
    def validate_dates(row):
        dob = pd.to_datetime(row['Date of Birth'])
        test_date = pd.to_datetime(row['Test Date'])
        if test_date < dob:
            return pd.Series({
                'Date of Birth': test_date,
                'Test Date': dob
            })
        return row[['Date of Birth', 'Test Date']]
    
    df[['Date of Birth', 'Test Date']] = df.apply(validate_dates, axis=1)
    return df

# Sidebar: Group Template
st.sidebar.header("Group Calculator")
st.sidebar.write("Download this template to add your data for many individuals.")
with open("Group_template.csv", "rb") as template_file:
    st.sidebar.download_button(
        label="Download Template",
        data=template_file,
        file_name="group_template.csv",
        mime="text/csv"
    )

# Main Content
st.markdown('<h1 class="main-header">Group Calculator</h1>', unsafe_allow_html=True)

# File Upload
uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

if uploaded_file is not None:
    # Read CSV
    df = pd.read_csv(uploaded_file)
    
    # Validate and fix dates
    df = validate_and_fix_dates(df)
    
    # Process Data
    results = []
    
    for index, row in df.iterrows():
        try:
            # Extract Data
            name = row['Name']
            gender = row['Gender']
            dob = pd.to_datetime(row['Date of Birth'])
            test_date = pd.to_datetime(row['Test Date'])
            body_mass_kg = float(row['Body Mass (kg)'])
            standing_height_cm = float(row['Standing Height (cm)'])
            mothers_height_cm = float(row["Mother's Height (cm)"])
            fathers_height_cm = float(row["Father's Height (cm)"])

            # Calculate Values
            chronological_age_val = chronological_age(dob, test_date)
            rounded_age_val = rounded_age(chronological_age_val)
            body_mass_lbs = kg_to_lbs(body_mass_kg)
            standing_height_inches = cm_to_inches(standing_height_cm)
            height_coefficient = get_height_coefficient(standing_height_inches)
            weight_coefficient = get_weight_coefficient(body_mass_lbs)
            mothers_height_inches = cm_to_inches(mothers_height_cm)
            adjusted_mother_height = adjust_mother_height_inches(mothers_height_inches)
            adjusted_mother_height_cm = inches_to_cm(adjusted_mother_height)
            fathers_height_inches = cm_to_inches(fathers_height_cm)
            adjusted_father_height = adjust_father_height_inches(fathers_height_inches)
            adjusted_father_height_cm = inches_to_cm(adjusted_father_height)
            midparent_height_cm = calculate_midparent_height_cm(adjusted_mother_height_cm, adjusted_father_height_cm)
            midparent_coefficient = get_midparent_coefficient(midparent_height_cm)
            intersect_val = get_intersect(height_coefficient, weight_coefficient, midparent_coefficient)
            predicted_height_cm = calculate_predicted_adult_height_cm(intersect_val)
            percent_predicted_height = calculate_percent_predicted_height(standing_height_cm, predicted_height_cm)
            biological_age_val = calculate_biological_age(percent_predicted_height)
            ba_ca_val = calculate_ba_ca(biological_age_val, chronological_age_val)
            timing_val = calculate_timing(ba_ca_val)
            alt_timing_val = calculate_alt_timing(ba_ca_val)
            maturity_status_val = calculate_maturity_status(percent_predicted_height)
            lower_50 = calculate_lower_bound_50(predicted_height_cm, rounded_age_val)
            upper_50 = calculate_upper_bound_50(predicted_height_cm, rounded_age_val)
            lower_90 = calculate_lower_bound_90(predicted_height_cm, rounded_age_val)
            upper_90 = calculate_upper_bound_90(predicted_height_cm, rounded_age_val)

            # Append Results
            results.append({
                "Name": name,
                "Gender": gender,
                "Date of Birth": dob.strftime('%Y-%m-%d'),
                "Test Date": test_date.strftime('%Y-%m-%d'),
                "Body Mass (kg)": body_mass_kg,
                "Standing Height (cm)": standing_height_cm,
                "Mother's Height (cm)": mothers_height_cm,
                "Father's Height (cm)": fathers_height_cm,
                "Chronological Age": chronological_age_val,
                "Biological Age": biological_age_val,
                "BA-CA": ba_ca_val,
                "Predicted Adult Height (cm)": predicted_height_cm,
                "Percent of Adult Height": percent_predicted_height,
                "Maturity Status": maturity_status_val,
                "Timing": timing_val,
                "Alt. Timing": alt_timing_val,
                "50% Lower Bound": lower_50,
                "50% Upper Bound": upper_50,
                "90% Lower Bound": lower_90,
                "90% Upper Bound": upper_90
            })

        except Exception as e:
            st.error(f"Error processing row {index + 1}: {e}")

    # Convert Results to DataFrame
    results_df = pd.DataFrame(results)

    # Display Results
    st.markdown('<h2 class="section-title">Results for Group</h2>', unsafe_allow_html=True)
    st.dataframe(results_df)

    # Sidebar: Download Results
    st.sidebar.download_button(
        label="Download Results as CSV",
        data=results_df.to_csv(index=False),
        file_name="group_results.csv",
        mime="text/csv"
    )
