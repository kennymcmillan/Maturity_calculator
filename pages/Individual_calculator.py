import streamlit as st
import pandas as pd
from datetime import datetime

# Complete module of all validated functions so far
import pandas as pd


def chronological_age(dob, test_date):
    """Excel: =IF(C2="","",YEARFRAC(C2,D2))"""
    if pd.isna(dob) or pd.isna(test_date):
        return ""
    days_diff = (test_date - dob).days
    return days_diff / 365.25

def rounded_age(age):
    """Excel: =MROUND(E2, 0.5)"""
    if pd.isna(age):
        return ""
    return round(age / 0.5) * 0.5

def kg_to_lbs(kg):
    """Excel: =G2*2.205"""
    if pd.isna(kg):
        return ""
    return kg * 2.205

def cm_to_inches(cm):
    """Excel: =I2*0.393701"""
    if pd.isna(cm):
        return ""
    return cm * 0.393701

def get_height_coefficient(gender, rounded_age):
    """Excel: IF/INDEX/MATCH formula for height coefficient"""
    metric_coef = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Metric coefficients')
    
    if gender == "Male":
        try:
            match_idx = metric_coef['Age'].eq(rounded_age).idxmax()
            return metric_coef.iloc[match_idx]['Stature (in)']
        except:
            return "Not Found"
    elif gender == "Female":
        try:
            match_idx = metric_coef['Age.1'].eq(rounded_age).idxmax()
            return metric_coef.iloc[match_idx]['Height']
        except:
            return "Not Found"
    return ""

def get_weight_coefficient(gender, rounded_age):
    """Excel: IF/INDEX/MATCH formula for weight coefficient"""
    metric_coef = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Metric coefficients')
    
    if gender == "Male":
        try:
            match_idx = metric_coef['Age'].eq(rounded_age).idxmax()
            return metric_coef.iloc[match_idx]['Weight (lb)']
        except:
            return "Not Found"
    elif gender == "Female":
        try:
            match_idx = metric_coef['Age.1'].eq(rounded_age).idxmax()
            return metric_coef.iloc[match_idx]['Weight']
        except:
            return "Not Found"
    return ""

def adjust_mother_height_inches(mother_height_inches):
    """Excel: =2.803+(0.953*N2)"""
    if pd.isna(mother_height_inches):
        return ""
    return 2.803 + (0.953 * mother_height_inches)

def inches_to_cm(inches):
    """Excel: =O2*2.54"""
    if pd.isna(inches):
        return ""
    return inches * 2.54

def adjust_father_height_inches(father_height_inches):
    """Excel: =2.316+(0.955*R2)"""
    if pd.isna(father_height_inches):
        return ""
    return 2.316 + (0.955 * father_height_inches)

def calculate_midparent_height_cm(adj_mother_cm, adj_father_cm):
    """Excel: Average of adjusted parent heights"""
    if pd.isna(adj_mother_cm) or pd.isna(adj_father_cm):
        return ""
    return (adj_mother_cm + adj_father_cm) / 2

def get_midparent_coefficient(gender, rounded_age):
    """Excel: IF/INDEX/MATCH formula for midparent coefficient"""
    metric_coef = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Metric coefficients')
    
    if gender == "Male":
        try:
            match_idx = metric_coef['Age'].eq(rounded_age).idxmax()
            return metric_coef.iloc[match_idx]['Midparent Stature (in)']
        except:
            return "Not Found"
    elif gender == "Female":
        try:
            match_idx = metric_coef['Age.1'].eq(rounded_age).idxmax()
            return metric_coef.iloc[match_idx]['Md parent']
        except:
            return "Not Found"
    return ""

def calculate_midparent_inches(gender, midparent_cm):
    """Excel: =IFS(B2="Male",U2*0.393701+2.5,B2="Female",U2*0.393701-2.5)"""
    if pd.isna(midparent_cm):
        return ""
    
    inches = midparent_cm * 0.393701
    if gender == "Male":
        return inches + 2.5
    elif gender == "Female":
        return inches - 2.5
    return ""

def get_intersect(gender, rounded_age):
    """Excel: IF/INDEX/MATCH formula for intersect value"""
    metric_coef = pd.read_excel('Maturation_calculator.xlsx', sheet_name='Metric coefficients')
    
    if gender == "Male":
        try:
            match_idx = metric_coef['Age'].eq(rounded_age).idxmax()
            return metric_coef.iloc[match_idx]['Beta']
        except:
            return "Not Found"
    elif gender == "Female":
        try:
            match_idx = metric_coef['Age.1'].eq(rounded_age).idxmax()
            return metric_coef.iloc[match_idx]['Intersect']
        except:
            return "Not Found"
    return ""

def calculate_predicted_adult_height_cm(intersect, height_coef, height_cm, weight_coef, weight_kg, midparent_coef, midparent_cm):
    """Excel: =X2+(J2*I2)+(L2*G2)+(V2*U2)"""
    if any(pd.isna([intersect, height_coef, height_cm, weight_coef, weight_kg, midparent_coef, midparent_cm])):
        return ""
    
    return intersect + (height_coef * height_cm) + (weight_coef * weight_kg) + (midparent_coef * midparent_cm)

def calculate_percent_predicted_height(current_height_cm, predicted_height_cm):
    """Excel: =IF(Y2=" ", " ", (I2/Y2*100))"""
    if pd.isna(current_height_cm) or pd.isna(predicted_height_cm) or predicted_height_cm == "":
        return ""
    return (current_height_cm / predicted_height_cm) * 100

def calculate_biological_age(gender, percent_predicted_height, sa_df):
    """
    Excel: =IFS(
        B2="Male", XLOOKUP(0, ABS(SA!$C$2:$C$218 - Input!Z2), SA!$A$2:$A$218, " ", 1),
        B2="Female", XLOOKUP(0, ABS(SA!$E$2:$E$218 - Input!Z2), SA!$A$2:$A$218, " ", 1)
    )
    """
    if pd.isna(percent_predicted_height) or percent_predicted_height == "":
        return ""
    
    if gender == "Male":
        pah_col = '%PAH Males'
    elif gender == "Female":
        pah_col = '%PAH females'
    else:
        return ""
    
    # Calculate absolute differences
    abs_diff = abs(sa_df[pah_col] - percent_predicted_height)
    
    # Find the index of minimum difference
    min_diff_idx = abs_diff.idxmin()
    
    # Return corresponding age
    return sa_df.loc[min_diff_idx, 'Age']

def calculate_ba_ca(chronological_age, biological_age):
    """Excel: =IF(E2=" ", " ",AA2-E2)"""
    if pd.isna(chronological_age) or pd.isna(biological_age) or chronological_age == "" or biological_age == "":
        return ""
    return biological_age - chronological_age

def calculate_timing(ba_ca):
    """Excel: =IFS(AB2=" "," ", AB2>0.5,"Early",AB2<=-0.5,"Late",AND(AB2>=-0.5,AB2<=0.5),"On Time")"""
    if pd.isna(ba_ca) or ba_ca == "":
        return ""
    if ba_ca > 0.5:
        return "Early"
    elif ba_ca <= -0.5:
        return "Late"
    else:
        return "On Time"

def calculate_alt_timing(ba_ca):
    """Excel: =IFS(AB2=" "," ", AB2>1,"Early",AB2<=-1,"Late",AND(AB2>=-1,AB2<=1),"On Time")"""
    if pd.isna(ba_ca) or ba_ca == "":
        return ""
    if ba_ca > 1:
        return "Early"
    elif ba_ca <= -1:
        return "Late"
    else:
        return "On Time"

def calculate_maturity_status(percent_predicted_height):
    """Excel: =IF(Z3<=88, "Pre-PHV", IF(Z3<=95, "Circa-PHV", "Post PHV"))"""
    if pd.isna(percent_predicted_height) or percent_predicted_height == "":
        return ""
    if percent_predicted_height <= 88:
        return "Pre-PHV"
    elif percent_predicted_height <= 95:
        return "Circa-PHV"
    else:
        return "Post PHV"

def calculate_lower_bound_50(predicted_height_cm, rounded_age):
    """Excel: =Y2 - IFERROR(INDEX(Errors!$B$2:$B$100, MATCH(F2 + 0.5, Errors!$A$2:$A$100, 0)), 0)"""
    if pd.isna(predicted_height_cm) or pd.isna(rounded_age) or predicted_height_cm == "" or rounded_age == "":
        return ""
    
    try:
        # Find the closest age match in errors table for rounded_age + 0.5
        target_age = rounded_age + 0.5
        closest_age_idx = errors_df['Age'].searchsorted(target_age)
        
        if closest_age_idx >= len(errors_df):
            return predicted_height_cm  # Return original value if no match found
            
        error_value = errors_df.iloc[closest_age_idx][0.5]  # 0.5 is the column name for 50% bounds
        return predicted_height_cm - error_value
    except:
        return predicted_height_cm  # Return original value if any error occurs

def calculate_upper_bound_50(predicted_height_cm, rounded_age):
    """Excel: =Y2 + IFERROR(INDEX(Errors!$B$2:$B$100, MATCH(F2 + 0.5, Errors!$A$2:$A$100, 0)), 0)"""
    if pd.isna(predicted_height_cm) or pd.isna(rounded_age) or predicted_height_cm == "" or rounded_age == "":
        return ""
    
    try:
        # Find the closest age match in errors table for rounded_age + 0.5
        target_age = rounded_age + 0.5
        closest_age_idx = errors_df['Age'].searchsorted(target_age)
        
        if closest_age_idx >= len(errors_df):
            return predicted_height_cm  # Return original value if no match found
            
        error_value = errors_df.iloc[closest_age_idx][0.5]  # 0.5 is the column name for 50% bounds
        return predicted_height_cm + error_value
    except:
        return predicted_height_cm  # Return original value if any error occurs

def calculate_lower_bound_90(predicted_height_cm, rounded_age):
    """Excel: =Y2 - IFERROR(INDEX(Errors!$C$2:$C$100, MATCH(F2 + 0.5, Errors!$A$2:$A$100, 0)), 0)"""
    if pd.isna(predicted_height_cm) or pd.isna(rounded_age) or predicted_height_cm == "" or rounded_age == "":
        return ""
    
    try:
        # Find the closest age match in errors table for rounded_age + 0.5
        target_age = rounded_age + 0.5
        closest_age_idx = errors_df['Age'].searchsorted(target_age)
        
        if closest_age_idx >= len(errors_df):
            return predicted_height_cm  # Return original value if no match found
            
        error_value = errors_df.iloc[closest_age_idx][0.9]  # 0.9 is the column name for 90% bounds
        return predicted_height_cm - error_value
    except:
        return predicted_height_cm  # Return original value if any error occurs

# Implement Upper bound 90% calculation
def calculate_upper_bound_90(predicted_height_cm, rounded_age):
    """Excel: =Y2 + IFERROR(INDEX(Errors!$C$2:$C$100, MATCH(F2 + 0.5, Errors!$A$2:$A$100, 0)), 0)"""
    if pd.isna(predicted_height_cm) or pd.isna(rounded_age) or predicted_height_cm == "" or rounded_age == "":
        return ""
    
    try:
        # Find the closest age match in errors table for rounded_age + 0.5
        target_age = rounded_age + 0.5
        closest_age_idx = errors_df['Age'].searchsorted(target_age)
        
        if closest_age_idx >= len(errors_df):
            return predicted_height_cm  # Return original value if no match found
            
        error_value = errors_df.iloc[closest_age_idx][0.9]  # 0.9 is the column name for 90% bounds
        return predicted_height_cm + error_value
    except:
        return predicted_height_cm  # Return original value if any error occurs



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
        .sub-section-title {{
            font-size: 20px;
            color: {WHITE};
            margin-top: 10px;
            margin-bottom: 5px;
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
   # st.markdown(f'<p class="result-text">Alt. Timing: {alt_timing_val}</p>', unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">Height Bounds</h2>', unsafe_allow_html=True)
    st.markdown('<h3 class="sub-section-title">50% Confidence Interval</h3>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Lower: {lower_50:.1f} cm</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-text">Upper: {upper_50:.1f} cm</p>', unsafe_allow_html=True)
    st.markdown('<h3 class="sub-section-title">90% Confidence Interval</h3>', unsafe_allow_html=True)
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

