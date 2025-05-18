# Offset-ink-calculator-
Coding by Robin Creative Lab (Experimental)
import streamlit as st

# Page configuration
st.set_page_config(page_title="Hang Tag Ink Estimator", layout="centered")

# Title
st.title("🎨 Hang Tag Ink Estimator")
st.subheader("Offset Ink Calculation Using ISO Standard")

# Input section
st.markdown("### 📥 Input Parameters")

tag_width_mm = st.number_input("Tag Width (mm)", min_value=1.0, value=100.0)
tag_height_mm = st.number_input("Tag Height (mm)", min_value=1.0, value=50.0)
quantity = st.number_input("Quantity", min_value=1, value=10000)

sheet_width_in = st.number_input("Raw Sheet Width (inches)", min_value=1.0, value=20.0)
sheet_height_in = st.number_input("Raw Sheet Height (inches)", min_value=1.0, value=28.0)

num_colors = st.number_input("Number of Colors (CMYK + Spot)", min_value=1, value=5)
coverage_percent = st.slider("Average Ink Coverage per Color (%)", 1, 100, 30)

# Calculation logic
total_area_m2 = (tag_width_mm * tag_height_mm * quantity) / 1_000_000
ink_per_color_g = total_area_m2 * (coverage_percent / 100) * 2  # 2g/m² ISO standard
total_ink_g = ink_per_color_g * num_colors

# Output section
st.markdown("### 📊 Estimated Results")
st.write(f"**Total Printed Area:** `{total_area_m2:.2f}` m²")
st.write(f"**Ink Required per Color:** `{ink_per_color_g:.2f}` grams")
st.write(f"**Total Ink Required (All Colors):** `{total_ink_g:.2f}` grams")

# Footer
st.markdown("---")
st.caption("Developed by Robin • Powered by Streamlit")
