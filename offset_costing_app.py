# offset_costing_app.py

import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# App branding
st.set_page_config(page_title="Offset Costing by Robin", layout="centered")

st.markdown("""
# 🖨️ Robin Creative Lab Presents  
### 📌 Project Name: Automated Cost Management Solutions  
**Department**: Offset Print  
_Note: This is a Demonstration with one module. We can customize based on your requirement and your product line._

📞 For more information or custom-made apps:  
👉 WhatsApp: +88 01746 927 626  
📧 Email: robin.ual@gmail.com  
🔗 [LinkedIn/syeed-robin](https://linkedin.com/in/syeed-robin)
""")

# ---- LOGIN SYSTEM ----
def login():
    st.sidebar.title("🔐 Login")
    login_type = st.sidebar.radio("Select login type", ["Admin", "Registered User", "Guest"])

    if login_type == "Admin":
        email = st.sidebar.text_input("Admin Email")
        password = st.sidebar.text_input("Password", type="password")
        if email == "robin.ual@gmail.com" and password == "01746927626":
            return "Admin"
        else:
            st.sidebar.warning("Enter correct admin credentials.")

    elif login_type == "Registered User":
        code = st.sidebar.text_input("Enter Approval Code")
        if code == "AUTHORIZED":
            return "User"
        else:
            st.sidebar.warning("Approval code required. Contact admin.")

    elif login_type == "Guest":
        name = st.sidebar.text_input("Your Name")
        email = st.sidebar.text_input("Email")
        if name and email:
            st.sidebar.success(f"Welcome, {name}")
            return "Guest"

    return None

user_role = login()
if not user_role:
    st.stop()

# ---- FORM INPUT ----
st.header("🧾 Costing Input Form")

col1, col2 = st.columns(2)
with col1:
    item_name = st.text_input("Item Name")
    width = st.number_input("Width (mm)", min_value=1.0)
    length = st.number_input("Length (mm)", min_value=1.0)
    quantity = st.number_input("Order Quantity", min_value=1)
    wastage = st.slider("Wastage (%)", min_value=0, max_value=20, value=5)

with col2:
    paper_type = st.selectbox("Paper Type", ["Art Card", "Swedish Board", "Kraft"])
    paper_dimensions = st.selectbox("Printing Paper Size (inches)", ["13x19", "11x14", "9x13", "14x22"])
    print_type = st.selectbox("Printing Type", ["Offset", "Digital"])
    spot_color = st.number_input("Spot Colors", min_value=0)
    cmyk = st.checkbox("Use CMYK (adds 4 colors)")

# GSM and pricing
paper_gsm = 300
paper_prices = {
    "Art Card": {"price": 30, "size": (22, 28)},
    "Swedish Board": {"price": 35, "size": (28, 44)},
    "Kraft": {"price": 40, "size": (31.5, 41.5)}
}

# Convert inches to mm
def inch_to_mm(val): return val * 25.4
full_sheet = paper_prices[paper_type]["size"]
full_area_in = full_sheet[0] * full_sheet[1]
print_sheet = tuple(map(int, paper_dimensions.split("x")))
print_area = print_sheet[0] * print_sheet[1]
product_area_mm = width * length
product_area_in = product_area_mm / 645.16  # mm² to in²

# Colors
total_colors = spot_color + (4 if cmyk else 0)
prod_qty = int(quantity * (1 + wastage / 100))
ups = int((inch_to_mm(print_sheet[0]) // width) * (inch_to_mm(print_sheet[1]) // length))
total_sheets = int((prod_qty + ups - 1) / ups)

# Print Cost
if print_type == "Digital":
    print_cost_per_sheet = (print_area * 3.9) / (13 * 19)  # normalize
else:
    print_cost_per_sheet = (total_sheets / 1000) * 300 * total_colors

# Paper price
sheet_price = paper_prices[paper_type]["price"]
total_paper_price = sheet_price * total_sheets

# Additional costs
special_sq_cost = st.number_input("Other Add-on Cost/sq.in", min_value=0.0)
addon_total = special_sq_cost * print_area * prod_qty / ups
additional_cost = 0.10 * (total_paper_price + print_cost_per_sheet + addon_total)

overhead_percent = st.selectbox("Overhead Cost (%)", [10, 15, 20])
overhead_cost = (overhead_percent / 100) * (total_paper_price + print_cost_per_sheet)

profit_margin = st.number_input("Profit Margin (%)", min_value=0.0, max_value=100.0, value=10.0)

# Total cost
total_cost = total_paper_price + print_cost_per_sheet + addon_total + additional_cost + overhead_cost
final_price = total_cost * (1 + profit_margin / 100)

# Currency & Output
usd_rate = 109.50  # Example rate
price_bdt = final_price
price_usd = final_price / usd_rate

unit_type = st.selectbox("Unit Type", ["Per Pcs", "Dozen", "Thousand"])

if st.button("💡 Calculate"):
    st.success("Calculation Complete!")
    st.write(f"🧾 Production Quantity: {prod_qty}")
    st.write(f"📦 UPS: {ups}")
    st.write(f"🧻 Total Sheets Required: {total_sheets}")
    st.write(f"💰 Paper Cost: {total_paper_price:.2f} BDT")
    st.write(f"🖨️ Print Cost: {print_cost_per_sheet:.2f} BDT")
    st.write(f"🧾 Additional Cost: {additional_cost:.2f} BDT")
    st.write(f"🏷️ Total Cost: {total_cost:.2f} BDT")
    st.write(f"📈 Final Price: {price_bdt:.2f} BDT / {price_usd:.2f} USD")

    photo = st.file_uploader("Upload product photo", type=["jpg", "png"])
    if photo:
        st.image(Image.open(photo), width=300)

    # Save to CSV
    result = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Item Name": item_name,
        "Dimensions (mm)": f"{width}x{length}",
        "Quantity": quantity,
        "Production Qty": prod_qty,
        "Paper": paper_type,
        "Sheet Used": total_sheets,
        "Total Cost": round(total_cost, 2),
        "Final Price (BDT)": round(price_bdt, 2),
        "Final Price (USD)": round(price_usd, 2),
        "Unit": unit_type
    }

    df = pd.DataFrame([result])
    st.download_button("📥 Download Costing CSV", df.to_csv(index=False).encode(), file_name="offset_costing.csv")

if st.button("🔄 Reset"):
    st.experimental_rerun()
