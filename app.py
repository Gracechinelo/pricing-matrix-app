import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Home Business Pricing Matrix",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Sleek UI styling to appeal to modern creative entrepreneurs
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            div.stButton > button:first-child {
                background-color: #FF5A5F;
                color: #ffffff;
                width: 100%;
                font-weight: bold;
                border-radius: 8px;
                border: none;
                padding: 10px;
            }
            div.stButton > button:first-child:hover {
                background-color: #e04f53;
                color: #ffffff;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 3. Header
st.title("🍓 Home Business Pricing Matrix")
st.markdown("Ensure your handmade products are *actually* profitable. Factor in materials, labor, and platform fees instantly.")
st.divider()

# 4. Region & Currency Setup
col_reg, col_cur = st.columns(2)
with col_reg:
    region = st.selectbox("Target Market / Platform Location", ["United States (US)", "United Kingdom (UK)"])
with col_cur:
    currency = "£" if "UK" in region else "$"

# 5. Cost Inputs
st.subheader("1. Production Costs")
col1, col2 = st.columns(2)

with col1:
    material_cost = st.number_input(f"Raw Materials Cost ({currency})", min_value=0.0, value=5.00, step=0.50, format="%.2f")
    packaging_cost = st.number_input(f"Packaging & Shipping Supplies ({currency})", min_value=0.0, value=1.50, step=0.50, format="%.2f")

with col2:
    time_spent = st.number_input("Time to Make One Item (Hours)", min_value=0.1, value=0.5, step=0.1)
    hourly_rate = st.number_input(f"Your Desired Hourly Wage ({currency})", min_value=0.0, value=15.00, step=1.00, format="%.2f")

# Calculate base cost of goods sold (COGS)
labor_cost = time_spent * hourly_rate
base_cogs = material_cost + packaging_cost + labor_cost

st.divider()

# 6. Platform Fees & Retail Strategy
st.subheader("2. Selling Platform & Listed Price")
col3, col4 = st.columns(2)

with col3:
    platform = st.selectbox("Where are you selling?", ["Etsy", "Shopify", "Stripe / Direct / Craft Fair"])
with col4:
    # Give them a suggested baseline so they don't underprice
    suggested_retail = base_cogs * 2
    retail_price = st.number_input(f"Your Proposed Retail Price ({currency})", min_value=0.0, value=float(round(suggested_retail, 2)), step=1.00, format="%.2f")

# 7. Fee Calculation Logic
# Standardized fee structures for 2026 platform rates
if platform == "Etsy":
    # Etsy: $0.20 listing fee + 6.5% transaction fee + ~3-4% payment processing fee
    listing_fee = 0.20 if currency == "$" else 0.17
    platform_fees = listing_fee + (retail_price * 0.065) + (retail_price * 0.04)
elif platform == "Shopify":
    # Shopify Basic Plan assumed: ~2.9% + $0.30 processing fee
    fixed_fee = 0.30 if currency == "$" else 0.25
    platform_fees = (retail_price * 0.029) + fixed_fee
else:
    # Direct/Stripe: ~2.9% + $0.30
    fixed_fee = 0.30 if currency == "$" else 0.25
    platform_fees = (retail_price * 0.029) + fixed_fee

total_costs = base_cogs + platform_fees
net_profit = retail_price - total_costs
margin_percentage = (net_profit / retail_price * 100) if retail_price > 0 else 0

st.divider()

# 8. The Pricing Matrix Breakdown
if st.button("Generate Profit Matrix"):
    
    st.subheader("📊 Your Financial Breakdown")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Cost to Produce", f"{currency}{base_cogs:.2f}")
    m2.metric("Estimated Platform Fees", f"{currency}{platform_fees:.2f}")
    m3.metric("Total Expenses", f"{currency}{total_costs:.2f}")
    
    st.divider()
    
    if net_profit > 0:
        st.success(f"🎉 **Net Profit per Sale:** {currency}{net_profit:.2f} (Margin: {margin_percentage:.1f}%)")
        if margin_percentage < 20:
            st.warning("⚠️ Your profit margin is below 20%. Consider raising your retail price or sourcing cheaper materials to safeguard your business.")
        elif margin_percentage >= 50:
            st.info("💎 Excellent margins! This product is highly sustainable for your home business.")
    else:
        st.error(f"❌ **You are LOSING money!** Net Loss per Sale: {currency}{abs(net_profit):.2f}. Increase your retail price immediately.")