import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np

# -----------------------------
# Calculation Functions
# -----------------------------
def chronological_age(dob, test_date):
    if pd.isna(dob) or pd.isna(test_date):
        return np.nan
    days_diff = (test_date - dob).days
    return days_diff / 365.25

def rounded_age(age):
    if pd.isna(age):
        return np.nan
    return round(age / 0.5) * 0.5

def kg_to_lbs(kg):
    if pd.isna(kg):
        return np.nan
    return kg * 2.205

def cm_to_inches(cm):
    if pd.isna(cm):
        return np.nan
    return cm * 0.393701

def get_height_coefficient(gender, rounded_age_val):
    metric_coef = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Metric coefficients')
    if gender == "Male":
        try:
            match_idx = metric_coef['Age'].eq(rounded_age_val).idxmax()
            return metric_coef.iloc[match_idx]['Stature (in)']
        except:
            return np.nan
    elif gender == "Female":
        try:
            match_idx = metric_coef['Age.1'].eq(rounded_age_val).idxmax()
            return metric_coef.iloc[match_idx]['Height']
        except:
            return np.nan
    return np.nan

def get_weight_coefficient(gender, rounded_age_val):
    metric_coef = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Metric coefficients')
    if gender == "Male":
        try:
            match_idx = metric_coef['Age'].eq(rounded_age_val).idxmax()
            return metric_coef.iloc[match_idx]['Weight (lb)']
        except:
            return np.nan
    elif gender == "Female":
        try:
            match_idx = metric_coef['Age.1'].eq(rounded_age_val).idxmax()
            return metric_coef.iloc[match_idx]['Weight']
        except:
            return np.nan
    return np.nan

def adjust_mother_height_inches(mother_height_inches):
    if pd.isna(mother_height_inches):
        return np.nan
    return 2.803 + (0.953 * mother_height_inches)

def inches_to_cm(inches):
    if pd.isna(inches):
        return np.nan
    return inches * 2.54

def adjust_father_height_inches(father_height_inches):
    if pd.isna(father_height_inches):
        return np.nan
    return 2.316 + (0.955 * father_height_inches)

def calculate_midparent_height_cm(adj_mother_cm, adj_father_cm):
    if pd.isna(adj_mother_cm) or pd.isna(adj_father_cm):
        return np.nan
    return (adj_mother_cm + adj_father_cm) / 2

def get_midparent_coefficient(gender, rounded_age_val):
    metric_coef = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Metric coefficients')
    if gender == "Male":
        try:
            match_idx = metric_coef['Age'].eq(rounded_age_val).idxmax()
            return metric_coef.iloc[match_idx]['Midparent Stature (in)']
        except:
            return np.nan
    elif gender == "Female":
        try:
            match_idx = metric_coef['Age.1'].eq(rounded_age_val).idxmax()
            return metric_coef.iloc[match_idx]['Md parent']
        except:
            return np.nan
    return np.nan

def calculate_midparent_inches(gender, midparent_cm):
    if pd.isna(midparent_cm):
        return np.nan
    inches = midparent_cm * 0.393701
    if gender == "Male":
        return inches + 2.5
    elif gender == "Female":
        return inches - 2.5
    return np.nan

def get_intersect(gender, rounded_age_val):
    metric_coef = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Metric coefficients')
    if gender == "Male":
        try:
            match_idx = metric_coef['Age'].eq(rounded_age_val).idxmax()
            return metric_coef.iloc[match_idx]['Beta']
        except:
            return np.nan
    elif gender == "Female":
        try:
            match_idx = metric_coef['Age.1'].eq(rounded_age_val).idxmax()
            return metric_coef.iloc[match_idx]['Intersect']
        except:
            return np.nan
    return np.nan

def calculate_predicted_adult_height_cm(intersect, height_coef, height_cm, weight_coef, weight_kg, midparent_coef, midparent_height_cm):
    if any(pd.isna(x) for x in [intersect, height_coef, height_cm, weight_coef, weight_kg, midparent_coef, midparent_height_cm]):
        return np.nan
    return intersect + (height_coef * height_cm) + (weight_coef * weight_kg) + (midparent_coef * midparent_height_cm)

def calculate_percent_predicted_height(current_height_cm, predicted_height_cm):
    if pd.isna(current_height_cm) or pd.isna(predicted_height_cm) or predicted_height_cm == 0:
        return np.nan
    return (current_height_cm / predicted_height_cm) * 100

def calculate_biological_age(gender, percent_predicted_height, sa_df):
    if pd.isna(percent_predicted_height):
        return np.nan
    pah_col = '%PAH Males' if gender == "Male" else '%PAH females'
    abs_diff = abs(sa_df[pah_col] - percent_predicted_height)
    min_diff_idx = abs_diff.idxmin()
    return sa_df.loc[min_diff_idx, 'Age']

def calculate_ba_ca(chronological_age_val, biological_age_val):
    if pd.isna(chronological_age_val) or pd.isna(biological_age_val):
        return np.nan
    return biological_age_val - chronological_age_val

def calculate_timing(ba_ca_val):
    if pd.isna(ba_ca_val):
        return ""
    if ba_ca_val > 0.5:
        return "Early"
    elif ba_ca_val <= -0.5:
        return "Late"
    else:
        return "On Time"

def calculate_alt_timing(ba_ca_val):
    if pd.isna(ba_ca_val):
        return ""
    if ba_ca_val > 1:
        return "Early"
    elif ba_ca_val <= -1:
        return "Late"
    else:
        return "On Time"

def calculate_maturity_status(percent_predicted_height):
    if pd.isna(percent_predicted_height):
        return ""
    if percent_predicted_height <= 88:
        return "Pre-PHV"
    elif percent_predicted_height <= 95:
        return "Circa-PHV"
    else:
        return "Post PHV"

def calculate_lower_bound_50(predicted_height_cm, rounded_age_val):
    if pd.isna(predicted_height_cm) or pd.isna(rounded_age_val):
        return np.nan
    try:
        target_age = rounded_age_val + 0.5
        closest_age_idx = errors_df['Age'].searchsorted(target_age)
        if closest_age_idx >= len(errors_df):
            return predicted_height_cm
        error_value = errors_df.iloc[closest_age_idx][0.5]
        return predicted_height_cm - error_value
    except:
        return predicted_height_cm

def calculate_upper_bound_50(predicted_height_cm, rounded_age_val):
    if pd.isna(predicted_height_cm) or pd.isna(rounded_age_val):
        return np.nan
    try:
        target_age = rounded_age_val + 0.5
        closest_age_idx = errors_df['Age'].searchsorted(target_age)
        if closest_age_idx >= len(errors_df):
            return predicted_height_cm
        error_value = errors_df.iloc[closest_age_idx][0.5]
        return predicted_height_cm + error_value
    except:
        return predicted_height_cm

def calculate_lower_bound_90(predicted_height_cm, rounded_age_val):
    if pd.isna(predicted_height_cm) or pd.isna(rounded_age_val):
        return np.nan
    try:
        target_age = rounded_age_val + 0.5
        closest_age_idx = errors_df['Age'].searchsorted(target_age)
        if closest_age_idx >= len(errors_df):
            return predicted_height_cm
        error_value = errors_df.iloc[closest_age_idx][0.9]
        return predicted_height_cm - error_value
    except:
        return predicted_height_cm

def calculate_upper_bound_90(predicted_height_cm, rounded_age_val):
    if pd.isna(predicted_height_cm) or pd.isna(rounded_age_val):
        return np.nan
    try:
        target_age = rounded_age_val + 0.5
        closest_age_idx = errors_df['Age'].searchsorted(target_age)
        if closest_age_idx >= len(errors_df):
            return predicted_height_cm
        error_value = errors_df.iloc[closest_age_idx][0.9]
        return predicted_height_cm + error_value
    except:
        return predicted_height_cm

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

# -----------------------------
# Load Reference Data (cached)
# -----------------------------
@st.cache_data
def load_reference_data():
    errors = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Errors')
    sa = pd.read_excel('Maturation_calculator.xlsx', sheet_name='SA')
    metrics = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Metric coefficients')
    return errors, sa, metrics

errors_df, sa_df, metrics_df = load_reference_data()

# -----------------------------
# Main App Layout
# -----------------------------
st.title("Group Maturation Calculator")

st.sidebar.markdown("## Group Upload Template")
st.sidebar.markdown("""
Download this template to use for your group upload.  
Please upload as a CSV file, and dates should be in **dd/mm/yyyy** format.
""")

# Provide a button to download the template
template_path = "Group_template.csv"
try:
    with open(template_path, "rb") as f:
        st.sidebar.download_button(
            label="Download Group Template",
            data=f,
            file_name="Group_template.csv",
            mime="text/csv"
        )
except FileNotFoundError:
    st.sidebar.error("Template file not found. Please check the directory.")

# File uploader for group data
uploaded_file = st.sidebar.file_uploader("Upload Your Group CSV", type=["csv"])
if uploaded_file is not None:
    # Force "Name" to be read as string
    df = pd.read_csv(uploaded_file, dtype={'Name': str})

    df = validate_and_fix_dates(df)
    
    results = []
    for idx, row in df.iterrows():
        try:
            # Extract input values
            name = row['Name']
            gender = row['Gender']
            dob = pd.to_datetime(row['Date of Birth'])
            test_date = pd.to_datetime(row['Test Date'])
            body_mass_kg = pd.to_numeric(row['Body Mass (kg)'], errors='coerce')
            standing_height_cm = pd.to_numeric(row['Standing Height (cm)'], errors='coerce')
            mothers_height_cm = pd.to_numeric(row["Mother's Height (cm)"], errors='coerce')
            fathers_height_cm = pd.to_numeric(row["Father's Height (cm)"], errors='coerce')
            
            # Compute the various calculations
            chrono_age = chronological_age(dob, test_date)
            round_age = rounded_age(chrono_age)
            height_coef = get_height_coefficient(gender, round_age)
            weight_coef = get_weight_coefficient(gender, round_age)
            mother_inches = cm_to_inches(mothers_height_cm)
            father_inches = cm_to_inches(fathers_height_cm)
            adj_mother_cm = inches_to_cm(adjust_mother_height_inches(mother_inches))
            adj_father_cm = inches_to_cm(adjust_father_height_inches(father_inches))
            midparent_height = calculate_midparent_height_cm(adj_mother_cm, adj_father_cm)
            midparent_coef = get_midparent_coefficient(gender, round_age)
            intersect_val = get_intersect(gender, round_age)
            predicted_height = calculate_predicted_adult_height_cm(
                intersect_val, height_coef, standing_height_cm, weight_coef, body_mass_kg,
                midparent_coef, midparent_height
            )
            pct_predicted = calculate_percent_predicted_height(standing_height_cm, predicted_height)
            bio_age = calculate_biological_age(gender, pct_predicted, sa_df)
            ba_ca_val = calculate_ba_ca(chrono_age, bio_age)
            timing = calculate_timing(ba_ca_val)
            alt_timing = calculate_alt_timing(ba_ca_val)
            maturity_status = calculate_maturity_status(pct_predicted)
            lower_50 = calculate_lower_bound_50(predicted_height, round_age)
            upper_50 = calculate_upper_bound_50(predicted_height, round_age)
            lower_90 = calculate_lower_bound_90(predicted_height, round_age)
            upper_90 = calculate_upper_bound_90(predicted_height, round_age)
            
            # Store the results in a dictionary
            results.append({
                'Name': name,
                'Gender': gender,
                'Date of Birth': dob.strftime('%Y-%m-%d'),
                'Test Date': test_date.strftime('%Y-%m-%d'),
                'Body Mass (kg)': body_mass_kg,
                'Standing Height (cm)': standing_height_cm,
                "Mother's Height (cm)": mothers_height_cm,
                "Father's Height (cm)": fathers_height_cm,
                'Chronological Age': chrono_age,
                'Biological Age': bio_age,
                'BA-CA': ba_ca_val,
                'Predicted Adult Height (cm)': predicted_height,
                'Percent of Adult Height': pct_predicted,
                'Maturity Status': maturity_status,
                'Timing': timing,
                'Alt. Timing': alt_timing,
                '50% Lower Bound': lower_50,
                '50% Upper Bound': upper_50,
                '90% Lower Bound': lower_90,
                '90% Upper Bound': upper_90
            })
        except Exception as e:
            st.error(f"Error processing row {idx+1} ({row.get('Name', 'Unknown')}): {e}")
    
    # Convert results list into a DataFrame and display it
    results_df = pd.DataFrame(results)
    st.dataframe(results_df)
    
    # Create CSV data and add a download button
    csv_data = results_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download Results as CSV",
        data=csv_data,
        file_name="maturation_results.csv",
        mime="text/csv"
    )
