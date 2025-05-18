# offset_costing_app_v2.py
import streamlit as st
import pandas as pd
from datetime import datetime
import math

# Admin and registration data
ADMIN_EMAIL = "Robin.ual@gmail.com"
ADMIN_PASSWORD = "01746927626"
APPROVAL_CODE = "ROBINAPPROVE"

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_type" not in st.session_state:
    st.session_state.user_type = None

# Paper data
paper_types = {
    "Art Card": {"price": 30, "size": (22, 28)},
    "Swedish Board": {"price": 35, "size": (28, 44)},
    "Craft": {"price": 40, "size": (31.5, 41.5)}
}

print_sizes = {
    "13x19 in": (13, 19),
    "11x14 in": (11, 14),
    "9x13 in": (9, 13),
    "14x22 in": (14, 22)
}

exchange_rate = 110  # 1 USD = 110 BDT

# Authentication functions
def login():
    st.subheader("Login")
    username = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.user_type = "admin"
        else:
            st.warning("Enter correct admin credentials.")

def guest_login():
    st.subheader("Guest Access")
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    if st.button("Enter as Guest"):
        st.session_state.logged_in = True
        st.session_state.user_type = "guest"
        st.success(f"Welcome, {name}!")
        # Simulate email alert to admin
        print(f"New guest login: {name}, {email}")

def register():
    st.subheader("New User Registration")
    email = st.text_input("Email for Registration")
    password = st.text_input("Create Password", type="password")
    approval = st.text_input("Approval Code")
    if st.button("Register"):
        if approval == APPROVAL_CODE:
            st.success("Registration approved. You can now login.")
        else:
            st.error("Invalid approval code.")

# Main costing function
def calculate_cost():
    st.title("Offset Costing by Robin")
    st.caption("Robin Creative Lab Presents")
    st.markdown("""
    ### Project Name: Automated Cost Management Solutions  
    **Department:** Offset Print  
    **Note:** This is a demonstration module.
    """)

    with st.form("cost_form"):
        st.subheader("Input Parameters")

        item_name = st.text_input("Item Name")
        item_width = st.number_input("Item Width (mm)", min_value=1)
        item_length = st.number_input("Item Length (mm)", min_value=1)
        quantity = st.number_input("Order Quantity", min_value=1)
        wastage_percent = st.number_input("Wastage (%)", min_value=0, value=5)

        prod_qty = math.ceil(quantity * (1 + wastage_percent / 100))
        paper_type = st.selectbox("Paper Type", list(paper_types.keys()))
        paper_gsm = 300  # fixed for this model

        # Printing Colors
        spot_color = st.number_input("Spot Colors", min_value=0, value=0)
        cmyk = st.checkbox("Use CMYK?")
        print_color_count = spot_color + (4 if cmyk else 0)

        print_size_label = st.selectbox("Printing Paper Size", list(print_sizes.keys()))
        print_w, print_l = print_sizes[print_size_label]

        # Calculate UPS
        item_w_in = item_width / 25.4
        item_l_in = item_length / 25.4
        ups_x = math.floor(print_w / item_w_in)
        ups_y = math.floor(print_l / item_l_in)
        total_ups = ups_x * ups_y

        sheets_needed = math.ceil(prod_qty / total_ups)
        paper_price = paper_types[paper_type]["price"]
        total_paper_cost = sheets_needed * paper_price

        # Print Type
        print_type = st.selectbox("Print Type", ["Digital", "Offset"])
        if print_type == "Digital":
            area = print_w * print_l
            print_cost = area * print_color_count * sheets_needed * 0.02  # Est. 2 paisa/sq.inch
        else:
            print_cost = math.ceil((prod_qty / total_ups) * print_color_count / 1000) * 300

        # Special Effects
        st.markdown("**Other Finishing Options**")
        finishing = st.multiselect("Options", ["Spot", "Foil", "Emboss", "Deboss"])
        sqi_cost = st.number_input("Special Effect Cost per sq.in.", value=0.0)
        finishing_cost = sqi_cost * print_w * print_l * sheets_needed

        base_cost = total_paper_cost + print_cost + finishing_cost
        add_cost = base_cost * 0.10
        overhead = st.selectbox("Overhead (%)", [10, 15, 20])
        total_cost = base_cost + add_cost + (base_cost * overhead / 100)

        margin = st.number_input("Profit Margin (%)", min_value=0, value=15)
        final_price = total_cost * (1 + margin / 100)

        unit_option = st.selectbox("Unit", ["pcs", "dozen", "thousand"])
        divisor = {"pcs": 1, "dozen": 12, "thousand": 1000}[unit_option]
        price_per_unit = final_price / (prod_qty / divisor)
        price_usd = price_per_unit / exchange_rate

        # Image Upload
        img = st.file_uploader("Upload Product Image", type=["jpg", "png"])

        submitted = st.form_submit_button("Calculate")
        if submitted:
            st.success("Calculation Complete ✅")
            st.metric("Final Price (BDT)", f"{price_per_unit:.2f} / {unit_option}")
            st.metric("Price in USD", f"{price_usd:.2f} / {unit_option}")
            st.write("Production Quantity:", prod_qty)
            st.write("Total Paper Sheets:", sheets_needed)
            st.write("Total Paper Cost:", total_paper_cost)
            st.write("Print Cost:", print_cost)
            st.write("Special Finishing Cost:", finishing_cost)
            st.write("Additional Cost (10%):", add_cost)
            st.write("Overhead Cost:", base_cost * overhead / 100)
            st.write("Total Cost:", total_cost)

            # Store Data
            output = {
                "Item": item_name,
                "Quantity": quantity,
                "Production Qty": prod_qty,
                "Paper Type": paper_type,
                "Paper Sheets": sheets_needed,
                "Print Cost": print_cost,
                "Total Cost (BDT)": final_price,
                "Final Unit Price (BDT)": price_per_unit,
                "Final Unit Price (USD)": price_usd,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            df = pd.DataFrame([output])
            st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="cost_summary.csv")

# Main App Flow
st.set_page_config(page_title="Offset Costing by Robin", layout="wide")
st.sidebar.title("Robin Creative Lab")
st.sidebar.markdown("[LinkedIn Profile](https://linkedin.com/in/syeed-robin)")

if not st.session_state.logged_in:
    st.sidebar.subheader("Login Options")
    auth_method = st.sidebar.radio("Choose Option", ["Admin Login", "Register", "Guest"])
    if auth_method == "Admin Login":
        login()
    elif auth_method == "Register":
        register()
    else:
        guest_login()
else:
    calculate_cost()
