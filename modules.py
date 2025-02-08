import streamlit as st
import pandas as pd
from datetime import datetime

# Load Data Function
@st.cache_data
def load_all_data():
    errors_df = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Errors')
    sa_df = pd.read_excel('Maturation_calculator.xlsx', sheet_name='SA')
    metric_coef = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Metric coefficients')
    return errors_df, sa_df, metric_coef

errors_df, sa_df, metric_coef = load_all_data()

# Function Definitions
def chronological_age(dob, test_date):
    if pd.isna(dob) or pd.isna(test_date):
        return ""
    return (test_date - dob).days / 365.25

def rounded_age(age):
    if pd.isna(age):
        return ""
    return round(age / 0.5) * 0.5

def kg_to_lbs(kg):
    if pd.isna(kg):
        return ""
    return float(kg) * 2.205

def cm_to_inches(cm):
    if pd.isna(cm):
        return ""
    return float(cm) * 0.393701

def inches_to_cm(inches):
    if pd.isna(inches):
        return ""
    return float(inches) * 2.54

def get_height_coefficient(gender, rounded_age):
    if gender == "Male":
        match_idx = metric_coef['Age'].eq(rounded_age).idxmax()
        return metric_coef.iloc[match_idx]['Stature (in)']
    elif gender == "Female":
        match_idx = metric_coef['Age.1'].eq(rounded_age).idxmax()
        return metric_coef.iloc[match_idx]['Height']
    return ""

def get_weight_coefficient(gender, rounded_age):
    if gender == "Male":
        match_idx = metric_coef['Age'].eq(rounded_age).idxmax()
        return metric_coef.iloc[match_idx]['Weight (lb)']
    elif gender == "Female":
        match_idx = metric_coef['Age.1'].eq(rounded_age).idxmax()
        return metric_coef.iloc[match_idx]['Weight']
    return ""

def adjust_mother_height_inches(mother_height_inches):
    if pd.isna(mother_height_inches):
        return ""
    return 2.803 + (0.953 * mother_height_inches)

def adjust_father_height_inches(father_height_inches):
    if pd.isna(father_height_inches):
        return ""
    return 2.316 + (0.955 * father_height_inches)

def calculate_midparent_height_cm(adj_mother_cm, adj_father_cm):
    if pd.isna(adj_mother_cm) or pd.isna(adj_father_cm):
        return ""
    return (adj_mother_cm + adj_father_cm) / 2

def get_intersect(gender, rounded_age):
    if gender == "Male":
        match_idx = metric_coef['Age'].eq(rounded_age).idxmax()
        return metric_coef.iloc[match_idx]['Beta']
    elif gender == "Female":
        match_idx = metric_coef['Age.1'].eq(rounded_age).idxmax()
        return metric_coef.iloc[match_idx]['Intersect']
    return ""

def calculate_predicted_adult_height_cm(intersect, height_coef, height_cm, weight_coef, weight_kg, midparent_coef, midparent_cm):
    if any(pd.isna([intersect, height_coef, height_cm, weight_coef, weight_kg, midparent_coef, midparent_cm])):
        return ""
    return intersect + (height_coef * height_cm) + (weight_coef * weight_kg) + (midparent_coef * midparent_cm)

def validate_and_fix_dates(df):
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

# Sidebar: Group Template
st.sidebar.header("Group Calculator")
st.sidebar.write("Download this template to add your data.")
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
    df = pd.read_csv(uploaded_file)

    # Validate and fix dates
    df = validate_and_fix_dates(df)

    # Process Data
    results = []
    
    for index, row in df.iterrows():
        try:
            name = row['Name']
            gender = str(row['Gender']).strip()
            dob = pd.to_datetime(row['Date of Birth'], errors='coerce')
            test_date = pd.to_datetime(row['Test Date'], errors='coerce')

            body_mass_kg = pd.to_numeric(row['Body Mass (kg)'], errors='coerce')
            standing_height_cm = pd.to_numeric(row['Standing Height (cm)'], errors='coerce')
            mothers_height_cm = pd.to_numeric(row["Mother's Height (cm)"], errors='coerce')
            fathers_height_cm = pd.to_numeric(row["Father's Height (cm)"], errors='coerce')

            if any(pd.isna([body_mass_kg, standing_height_cm, mothers_height_cm, fathers_height_cm])):
                st.warning(f"Skipping row {index+1} due to missing or invalid numeric values.")
                continue

            chronological_age_val = chronological_age(dob, test_date)
            rounded_age_val = rounded_age(chronological_age_val)

            body_mass_lbs = kg_to_lbs(body_mass_kg)
            standing_height_inches = cm_to_inches(standing_height_cm)

            mothers_height_inches = cm_to_inches(mothers_height_cm)
            fathers_height_inches = cm_to_inches(fathers_height_cm)

            adjusted_mother_height = adjust_mother_height_inches(mothers_height_inches)
            adjusted_father_height = adjust_father_height_inches(fathers_height_inches)

            adj_mother_cm = inches_to_cm(adjusted_mother_height)
            adj_father_cm = inches_to_cm(adjusted_father_height)

            midparent_height_cm = calculate_midparent_height_cm(adj_mother_cm, adj_father_cm)
            intersect_val = get_intersect(gender, rounded_age_val)
            predicted_height_cm = calculate_predicted_adult_height_cm(intersect_val, 1, standing_height_cm, 1, body_mass_kg, 1, midparent_height_cm)

            results.append({
                "Name": name,
                "Gender": gender,
                "Date of Birth": dob.strftime('%Y-%m-%d'),
                "Test Date": test_date.strftime('%Y-%m-%d'),
                "Body Mass (kg)": body_mass_kg,
                "Standing Height (cm)": standing_height_cm,
                "Predicted Adult Height (cm)": predicted_height_cm
            })

        except Exception as e:
            st.error(f"Error processing row {index + 1}: {e}")

    results_df = pd.DataFrame(results)
    st.markdown('<h2 style="color: green;">Results</h2>', unsafe_allow_html=True)
    st.dataframe(results_df)

    st.sidebar.download_button(
        label="Download Results as CSV",
        data=results_df.to_csv(index=False),
        file_name="group_results.csv",
        mime="text/csv"
    )
