import streamlit as st
import pandas as pd
from datetime import datetime

# Function Definitions
def chronological_age(dob, test_date):
    if pd.isna(dob) or pd.isna(test_date):
        return ""
    days_diff = (test_date - dob).days
    return days_diff / 365.25

def rounded_age(age):
    if pd.isna(age):
        return ""
    return round(age / 0.5) * 0.5

def kg_to_lbs(kg):
    if pd.isna(kg):
        return ""
    return float(kg) * 2.205  # Ensure conversion

def cm_to_inches(cm):
    if pd.isna(cm):
        return ""
    return float(cm) * 0.393701  # Ensure conversion

def validate_and_fix_dates(df):
    """Validate and fix dates in the dataframe to ensure test_date > date_of_birth"""
    def validate_dates(row):
        dob = pd.to_datetime(row['Date of Birth'], errors='coerce')
        test_date = pd.to_datetime(row['Test Date'], errors='coerce')
        if pd.isna(dob) or pd.isna(test_date):
            return pd.Series({'Date of Birth': dob, 'Test Date': test_date})
        if test_date < dob:
            return pd.Series({'Date of Birth': test_date, 'Test Date': dob})
        return pd.Series({'Date of Birth': dob, 'Test Date': test_date})
    
    df[['Date of Birth', 'Test Date']] = df.apply(validate_dates, axis=1)
    return df

@st.cache_data
def load_all_data():
    errors_df = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Errors')
    sa_df = pd.read_excel('Maturation_calculator.xlsx', sheet_name='SA')
    metrics_df = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Metric coefficients')
    return errors_df, sa_df, metrics_df

errors_df, sa_df, metrics_df = load_all_data()

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
st.markdown('<h1 style="text-align: center; color: green;">Group Calculator</h1>', unsafe_allow_html=True)

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
            gender = str(row['Gender']).strip()  # Ensure it's a string
            dob = pd.to_datetime(row['Date of Birth'], errors='coerce')
            test_date = pd.to_datetime(row['Test Date'], errors='coerce')

            # Convert to numeric values
            body_mass_kg = pd.to_numeric(row['Body Mass (kg)'], errors='coerce')
            standing_height_cm = pd.to_numeric(row['Standing Height (cm)'], errors='coerce')
            mothers_height_cm = pd.to_numeric(row["Mother's Height (cm)"], errors='coerce')
            fathers_height_cm = pd.to_numeric(row["Father's Height (cm)"], errors='coerce')

            # Skip rows with missing or invalid numeric values
            if any(pd.isna([body_mass_kg, standing_height_cm, mothers_height_cm, fathers_height_cm])):
                st.warning(f"Skipping row {index+1} due to missing or invalid numeric values.")
                continue

            # Calculate initial age values
            chronological_age_val = chronological_age(dob, test_date)
            rounded_age_val = rounded_age(chronological_age_val)

            # Convert measurements
            body_mass_lbs = kg_to_lbs(body_mass_kg)
            standing_height_inches = cm_to_inches(standing_height_cm)
            mothers_height_inches = cm_to_inches(mothers_height_cm)
            fathers_height_inches = cm_to_inches(fathers_height_cm)

            # Debugging: Print values for problematic rows
            st.write(f"Row {index+1} - Name: {name}, Height (cm): {standing_height_cm}, Weight (kg): {body_mass_kg}")

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
                "Rounded Age": rounded_age_val,
                "Body Mass (lbs)": body_mass_lbs,
                "Standing Height (inches)": standing_height_inches,
                "Mother's Height (inches)": mothers_height_inches,
                "Father's Height (inches)": fathers_height_inches
            })

        except Exception as e:
            st.error(f"Error processing row {index + 1}: {e}")

    # Convert Results to DataFrame
    results_df = pd.DataFrame(results)

    # Display Results
    st.markdown('<h2 style="color: green;">Results for Group</h2>', unsafe_allow_html=True)
    st.dataframe(results_df)

    # Sidebar: Download Results
    st.sidebar.download_button(
        label="Download Results as CSV",
        data=results_df.to_csv(index=False),
        file_name="group_results.csv",
        mime="text/csv"
    )
