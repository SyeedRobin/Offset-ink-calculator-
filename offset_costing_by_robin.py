
# Offset Costing by Robin Creative Lab
# Project: Automated Cost Management Solutions | Department: Offset Print


import streamlit as st
import pandas as pd
import datetime
import math
from fpdf import FPDF
import base64

# Login credentials
ADMIN_EMAIL = "robin.ual@gmail.com"
ADMIN_PASSWORD = "01746927626"
APPROVAL_CODE = "54321"

# App settings
st.set_page_config(page_title="Offset Costing by Robin Creative Lab", layout="wide")
st.title("Offset Costing by Robin Creative Lab")
st.caption("Automated Cost Management Solutions - Offset Print Department")

# Login system
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_type = ""

def login_ui():
    option = st.sidebar.radio("Login As", ["Admin", "Register", "Guest"])

    if option == "Admin":
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.user_type = "admin"
            else:
                st.sidebar.error("Invalid credentials")
    elif option == "Register":
        email = st.sidebar.text_input("New Email")
        password = st.sidebar.text_input("Set Password", type="password")
        code = st.sidebar.text_input("Approval Code")
        if st.sidebar.button("Register"):
            if code == APPROVAL_CODE:
                st.sidebar.success("Approved. Please login from Admin.")
            else:
                st.sidebar.error("Invalid approval code")
    elif option == "Guest":
        guest_name = st.sidebar.text_input("Your Name")
        guest_email = st.sidebar.text_input("Email")
        if st.sidebar.button("Enter as Guest"):
            st.session_state.logged_in = True
            st.session_state.user_type = "guest"
            st.sidebar.success("Welcome guest. Access granted.")

login_ui()

if not st.session_state.logged_in:
    st.warning("Please log in to use the application.")
    st.stop()

# PDF Generator
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Offset Costing Summary - Robin Creative Lab", ln=True, align="C")

    def chapter_body(self, data_dict):
        self.set_font("Arial", "", 10)
        for key, value in data_dict.items():
            self.cell(0, 10, f"{key}: {value}", ln=True)

    def print_chapter(self, data_dict):
        self.add_page()
        self.chapter_body(data_dict)

# Costing form
with st.form("costing_form"):
    st.subheader("Enter Item Details")
    item_name = st.text_input("Item Name")
    width_mm = st.number_input("Width (mm)", min_value=1)
    length_mm = st.number_input("Length (mm)", min_value=1)
    quantity = st.number_input("Quantity", min_value=1)
    wastage_percent = st.slider("Wastage (%)", 0, 100, 5)
    production_qty = math.ceil(quantity * (1 + wastage_percent / 100))

    paper_type = st.selectbox("Paper Type", ["Art Card", "Swedish Board", "Craft"])
    paper_prices = {"Art Card": 30, "Swedish Board": 35, "Craft": 40}
    paper_sizes = {"Art Card": (22, 28), "Swedish Board": (28, 44), "Craft": (31.5, 41.5)}

    print_size = st.selectbox("Printing Paper Size", ["13x19in", "11x14in", "9x13in", "14x22in"])
    size_map = {"13x19in": (13, 19), "11x14in": (11, 14), "9x13in": (9, 13), "14x22in": (14, 22)}
    print_w, print_l = size_map[print_size]

    st.subheader("Print Color")
    spot_color = st.number_input("Spot Colors", min_value=0)
    cmyk = st.checkbox("Use CMYK")
    total_color = spot_color + (4 if cmyk else 0)

    ups_x = print_w / (width_mm / 25.4)
    ups_y = print_l / (length_mm / 25.4)
    ups = int(ups_x) * int(ups_y)
    total_sheets = math.ceil(production_qty / ups)
    paper_price = total_sheets * paper_prices[paper_type]

    machine = st.selectbox("Printing Machine", ["Digital", "Offset"])
    if machine == "Digital":
        cost_per_sheet = 3.9 * total_color
        printing_cost = total_sheets * cost_per_sheet
    else:
        printing_cost = (production_qty / ups) * total_color / 1000 * 300

    st.subheader("Finishing")
    finishing = st.multiselect("Options", ["Spot", "Foil", "Emboss", "Deboss"])
    sqi_cost = st.number_input("Cost per Sq. Inch", value=0.0)
    other_cost = sqi_cost * (print_w * print_l) / ups * production_qty

    subtotal = paper_price + printing_cost + other_cost
    additional_cost = subtotal * 0.10
    overhead = st.selectbox("Overhead (%)", [10, 15, 20])
    overhead_cost = subtotal * overhead / 100
    total_cost = subtotal + additional_cost + overhead_cost

    profit_margin = st.number_input("Profit Margin (%)", value=15.0)
    final_price = total_cost * (1 + profit_margin / 100)
    unit_type = st.selectbox("Unit", ["pcs", "dozen", "thousand"])
    divisor = {"pcs": 1, "dozen": 12, "thousand": 1000}[unit_type]
    unit_price = final_price / (production_qty / divisor)
    usd_price = unit_price / 110

    image = st.file_uploader("Upload Item Image", type=["jpg", "png"])
    submitted = st.form_submit_button("Submit Costing")

    if submitted:
        st.success("Costing Submitted Successfully!")
        st.write(f"Total Paper Sheets: {total_sheets}")
        st.write(f"Total Paper Price: {paper_price:.2f} BDT")
        st.write(f"Printing Cost: {printing_cost:.2f} BDT")
        st.write(f"Other Cost: {other_cost:.2f} BDT")
        st.write(f"Total Cost: {total_cost:.2f} BDT")
        st.write(f"Final Price: {unit_price:.2f} BDT / {usd_price:.2f} USD per {unit_type}")

        df = pd.DataFrame([{
            "Item": item_name,
            "Width_mm": width_mm,
            "Length_mm": length_mm,
            "Quantity": quantity,
            "ProductionQty": production_qty,
            "TotalSheets": total_sheets,
            "TotalCostBDT": total_cost,
            "FinalPriceBDT": unit_price,
            "FinalPriceUSD": usd_price,
            "SubmittedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }])
        st.download_button("Download CSV", df.to_csv(index=False), file_name="costing_data.csv")

        # PDF Export
        pdf = PDF()
        summary_data = {
            "Item": item_name,
            "Dimensions (mm)": f"{width_mm} x {length_mm}",
            "Quantity": quantity,
            "Production Qty": production_qty,
            "Paper Type": paper_type,
            "Paper Price (BDT)": f"{paper_price:.2f}",
            "Printing Cost (BDT)": f"{printing_cost:.2f}",
            "Finishing Cost (BDT)": f"{other_cost:.2f}",
            "Total Cost (BDT)": f"{total_cost:.2f}",
            "Price per Unit (BDT)": f"{unit_price:.2f}",
            "Price per Unit (USD)": f"{usd_price:.2f}",
            "Date": datetime.datetime.now().strftime("%Y-%m-%d"),
        }
        pdf.print_chapter(summary_data)
        pdf_path = "/mnt/data/costing_summary_robin.pdf"
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
