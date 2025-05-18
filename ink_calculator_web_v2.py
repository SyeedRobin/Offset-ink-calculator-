
# Hang Tag Ink & Paper Estimator App
# Created by Robin | Robin Creative Lab

import streamlit as st
import pandas as pd
import math
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Hang Tag Ink & Paper Cost Estimator", layout="centered")

# --- TITLE ---
st.title("🧮 Hang Tag Ink & Paper Cost Estimator")
st.caption("Created by Robin | Robin Creative Lab")

# --- STATE INIT ---
if 'results' not in st.session_state:
    st.session_state['results'] = []

# --- INPUT FORM ---
with st.form("ink_paper_form"):
    st.markdown("### 📥 Input Parameters")

    col1, col2 = st.columns(2)
    with col1:
        tag_width_mm = st.number_input("Tag Width (mm)", min_value=1.0, value=100.0)
        sheet_type = st.selectbox("Select Paper Type", ["Art Card", "Swidish Board", "Craft"])
        quantity = st.number_input("Quantity", min_value=1, value=10000)
    with col2:
        tag_height_mm = st.number_input("Tag Height (mm)", min_value=1.0, value=50.0)
        num_colors = st.number_input("Number of Colors (CMYK + Spot)", min_value=1, value=5)
        coverage_percent = st.slider("Average Ink Coverage per Color (%)", 1, 100, 30)

    # --- BUTTONS ---
    submitted = st.form_submit_button("Calculate")
    reset = st.form_submit_button("Reset")

# --- PAPER DATA ---
paper_data = {
    "Art Card": {"price": 30, "width_in": 22, "height_in": 28},
    "Swidish Board": {"price": 35, "width_in": 28, "height_in": 44},
    "Craft": {"price": 40, "width_in": 31.5, "height_in": 41.5},
}

# --- RESET LOGIC ---
if reset:
    st.session_state['results'] = []
    st.experimental_rerun()

# --- CALCULATION ---
if submitted:
    # Area in m²
    total_area_m2 = (tag_width_mm * tag_height_mm * quantity) / 1_000_000
    ink_per_color_g = total_area_m2 * (coverage_percent / 100) * 2
    total_ink_g = ink_per_color_g * num_colors

    # Paper details
    sheet = paper_data[sheet_type]
    sheet_width_mm = sheet["width_in"] * 25.4
    sheet_height_mm = sheet["height_in"] * 25.4
    price_per_sheet = sheet["price"]

    tags_per_sheet = math.floor(sheet_width_mm / tag_width_mm) * math.floor(sheet_height_mm / tag_height_mm)
    required_sheets = math.ceil(quantity / tags_per_sheet)
    total_paper_cost = required_sheets * price_per_sheet

    result = {
        "Tag Size": f"{tag_width_mm}x{tag_height_mm} mm",
        "Qty": quantity,
        "Paper": sheet_type,
        "Tags/Sheet": tags_per_sheet,
        "Sheets Required": required_sheets,
        "Paper Cost (Tk)": total_paper_cost,
        "Total Ink (g)": round(total_ink_g, 2)
    }

    st.session_state['results'].append(result)

# --- DISPLAY RESULTS ---
if st.session_state['results']:
    st.markdown("### 📊 Results Summary")
    df = pd.DataFrame(st.session_state['results'])
    st.dataframe(df, use_container_width=True)

    # Export to CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📤 Export to CSV", csv, "ink_paper_estimation.csv", "text/csv")

    # Import data
    uploaded = st.file_uploader("📥 Import CSV", type=["csv"])
    if uploaded:
        imported_df = pd.read_csv(uploaded)
        st.session_state['results'] = imported_df.to_dict("records")
        st.experimental_rerun()
