import streamlit as st
import pandas as pd

# Set Page Config
st.set_page_config(
    page_title="Etsy True-Cost & Pricing Calculator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HIDE STREAMLIT BRANDING (AGGRESSIVE) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Nuke the floating Creator Badge and Toolbar */
            [data-testid="stCreatorProfile"] {display: none !important;}
            [data-testid="stToolbar"] {display: none !important;}
            .viewerBadge_container {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Custom Styling
st.markdown("""
<style>
    .reportview-container {
        font-family: 'Inter', sans-serif;
    }
    .metric-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #ffffff;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 800;
        color: #f59e0b;
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600;
        color: rgba(255, 255, 255, 0.7);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to strictly format currency outputs consistently across entire app
def format_currency(val, sym):
    return f"{sym}{val:,.2f}"

# Conversion Factors
DRY_CONV = {
    "g": 1.0,
    "kg": 1000.0,
    "oz": 28.349523,
    "lb": 453.59237,
}

LIQUID_CONV_US = {
    "ml": 1.0,
    "L": 1000.0,
    "fl oz": 29.5735296,
    "cup": 236.588237,
    "pt": 473.176473,
    "qt": 946.352946,
    "gal": 3785.41178,
}

LIQUID_CONV_UK = {
    "ml": 1.0,
    "L": 1000.0,
    "fl oz": 28.4130625,
    "pt": 568.26125,
    "qt": 1136.5225,
    "gal": 4546.09,
}

# Initialize session states
if "materials" not in st.session_state:
    st.session_state.materials = [
        {"name": "Organic Wax Beans", "type": "dry", "buy_qty": 5.0, "buy_unit": "lb", "cost": 24.99, "use_qty": 6.5, "use_unit": "oz"},
        {"name": "Luxury Fragrance Oil", "type": "liquid", "buy_qty": 8.0, "buy_unit": "fl oz", "cost": 15.50, "use_qty": 15.0, "use_unit": "ml"}
    ]

# Helper function to compute cost and yield
def compute_material_stats(mat, is_us, symbol):
    buy_qty = float(mat["buy_qty"])
    cost = float(mat["cost"])
    use_qty = float(mat["use_qty"])
    
    if buy_qty <= 0 or cost <= 0 or use_qty <= 0:
        return 0.0, 1.0, 0.0, "Invalid Inputs"
    
    # Select conversion tables
    if mat["type"] == "dry":
        buy_factor = DRY_CONV.get(mat["buy_unit"], 1.0)
        use_factor = DRY_CONV.get(mat["use_unit"], 1.0)
        base_unit = "g"
    else:
        table = LIQUID_CONV_US if is_us else LIQUID_CONV_UK
        buy_factor = table.get(mat["buy_unit"], 1.0)
        use_factor = table.get(mat["use_unit"], 1.0)
        base_unit = "ml"
        
    buy_total_base = buy_qty * buy_factor
    use_total_base = use_qty * use_factor
    
    # Multiplier/yield
    raw_yield = buy_total_base / use_total_base
    yield_val = max(1.0, int(raw_yield))
    
    # Cost per single item
    cost_per_item = cost / raw_yield if raw_yield > 0 else cost
    leftover = max(0.0, buy_total_base - (yield_val * use_total_base)) / use_factor
    
    walkthrough = (
        f"{buy_qty} {mat['buy_unit']} ({buy_total_base:.1f}{base_unit}) bought for {format_currency(cost, symbol)}. "
        f"Each craft uses {use_qty} {mat['use_unit']} ({use_total_base:.1f}{base_unit}). "
        f"Produces ~{raw_yield:.2f} items."
    )
    
    return cost_per_item, yield_val, leftover, walkthrough

# Title Column
st.title("⚖️ Etsy True-Cost & Pricing Calculator")
st.markdown("##### High-precision materials, labor, and UK/US shipping-fee pricing models")

# Setup Primary Columns
left_col, right_col = st.columns([7, 5])

with left_col:
    # 1. PROFILE SELECTOR
    st.markdown("### 🗺️ Business Profile & Location settings")
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        country = st.selectbox("Seller Location", ["United States (USD / Imperial)", "United Kingdom (GBP / Metric)"])
        is_us = (country == "United States (USD / Imperial)")
        currency = "USD" if is_us else "GBP"
        symbol = "$" if is_us else "£"
    with p_col2:
        target_margin = st.slider("Target Net Margin (%)", min_value=5, max_value=85, value=40, step=5) / 100.0
    with p_col3:
        if not is_us:
            apply_vat = st.checkbox("Register standard 20% VAT? (If checked, VAT is correctly processed on internal Etsy fees)", value=True)
        else:
            apply_vat = False
            st.markdown("<p style='color:grey; font-size:11px;'><br>US profile exempt from UK VAT rules</p>", unsafe_allow_html=True)

    st.markdown("<hr style='margin: 1.5rem 0; border: 0; border-top: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

    # 2. LABOUR TIMING
    st.markdown("### ⏱️ Hourly Craft & Packaging Labor Support")
    l_col1, l_col2 = st.columns(2)
    with l_col1:
        hourly_wage = st.number_input(f"Your Target Hourly Wage ({symbol}/hr)", min_value=0.0, value=15.0 if is_us else 11.5, step=0.50, format="%.2f")
    with l_col2:
        labor_time = st.number_input("Time Spent per Item (Minutes)", min_value=0.0, value=25.0, step=1.0)
    
    total_labor_cost = (labor_time / 60.0) * hourly_wage
    st.info(f"💡 Calculated internal labor cost: **{format_currency(total_labor_cost, symbol)}** per crafted item.")

    st.markdown("<hr style='margin: 1.5rem 0; border: 0; border-top: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

    # 3. INTERACTIVE MATERIAL BUILDER WITH MEASURE CONVERSIONS
    st.markdown("### 📦 Dynamic Material Recipe Designer")
    st.markdown(f"Define materials. The calculator handles complex UK/US **dry unit conversions (g, kg, oz, lb)** or **liquid/volume conversions (ml, L, fl oz, pt, qt, gal)** to determine precise yield costs per item.")

    # Show existing materials list
    mats_to_delete = []
    total_materials_cost = 0.0

    for i, mat in enumerate(st.session_state.materials):
        with st.expander(f"Material #{i+1}: {mat['name']} (Cost/item estimate)", expanded=True):
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                mat["name"] = st.text_input("Name", value=mat["name"], key=f"mat_name_{i}")
                mat["type"] = st.selectbox("Category", ["dry", "liquid"], index=0 if mat["type"] == "dry" else 1, key=f"mat_type_{i}")
            with mc2:
                mat["buy_qty"] = st.number_input(f"Bulk Buy Qty", min_value=0.01, value=float(mat["buy_qty"]), step=0.1, key=f"mat_buy_{i}")
                
                # Dynamic Units dropdowns
                if mat["type"] == "dry":
                    buy_units_opt = ["g", "kg", "oz", "lb"]
                else:
                    buy_units_opt = ["ml", "L", "fl oz", "cup", "pt", "qt", "gal"] if is_us else ["ml", "L", "fl oz", "pt", "gal"]
                
                mat["buy_unit"] = st.selectbox("Bulk Buy Unit", buy_units_opt, index=buy_units_opt.index(mat["buy_unit"]) if mat["buy_unit"] in buy_units_opt else 0, key=f"mat_buy_unit_{i}")
                mat["cost"] = st.number_input(f"Bulk Price ({symbol})", min_value=0.01, value=float(mat["cost"]), step=0.1, key=f"mat_cost_{i}")
            with mc3:
                mat["use_qty"] = st.number_input("Usage Per Item", min_value=0.01, value=float(mat["use_qty"]), step=0.1, key=f"mat_use_{i}")
                
                if mat["type"] == "dry":
                    use_units_opt = ["g", "kg", "oz", "lb"]
                else:
                    use_units_opt = ["ml", "L", "fl oz", "cup", "pt", "qt", "gal"] if is_us else ["ml", "L", "fl oz", "pt", "gal"]
                    
                mat["use_unit"] = st.selectbox("Usage Unit", use_units_opt, index=use_units_opt.index(mat["use_unit"]) if mat["use_unit"] in use_units_opt else 0, key=f"mat_use_unit_{i}")
                
                if st.button("🗑️ Remove", key=f"del_mat_{i}"):
                    mats_to_delete.append(i)
                    
            # Compute yield details
            cost_item, item_yield, leftover, walkthrough = compute_material_stats(mat, is_us, symbol)
            total_materials_cost += cost_item
            
            st.markdown(f"""
            <div style="background-color: rgba(245, 158, 11, 0.08); padding: 8px 12px; border-radius: 6px; font-size: 12px; border-left: 3px solid #f59e0b; margin-top: 8px;">
                <strong>💡 Multi-Unit Yield Assistant:</strong> {walkthrough}<br>
                <strong>💰 Projected Cost per Item:</strong> {format_currency(cost_item, symbol)} | 
                <strong>Leftover batch residues:</strong> {leftover:.3f} {mat['use_unit']}
            </div>
            """, unsafe_allow_html=True)

    # Delete flagged materials
    if mats_to_delete:
        for idx in sorted(mats_to_delete, reverse=True):
            st.session_state.materials.pop(idx)
        st.rerun()

    # Add extra raw material row button
    if st.button("➕ Add New Raw Material"):
        st.session_state.materials.append({
            "name": f"Material #{len(st.session_state.materials) + 1}",
            "type": "dry",
            "buy_qty": 1.0,
            "buy_unit": "lb" if is_us else "kg",
            "cost": 10.0,
            "use_qty": 1.0,
            "use_unit": "oz" if is_us else "g"
        })
        st.rerun()

    st.markdown("<hr style='margin: 1.5rem 0; border: 0; border-top: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

    # 4. PACKAGING & POSTAL DELIVERY
    st.markdown("### 📦 Delivery and Shipping Logistics")
    del_col1, del_col2, del_col3 = st.columns(3)
    with del_col1:
        packaging_cost = st.number_input(f"Packing Supplies / Custom Box ({symbol})", min_value=0.0, value=1.50, step=0.10)
    with del_col2:
        actual_postage = st.number_input(f"Your Postage / Courier Spent ({symbol})", min_value=0.0, value=4.50, step=0.10)
    with del_col3:
        shipping_charged = st.number_input(f"Shipping Fee Charged to Buyer ({symbol})", min_value=0.0, value=5.00, step=0.10)

    # Master Sum sums
    gross_cost_per_item = total_materials_cost + total_labor_cost + packaging_cost + actual_postage

# 5. HIGH ACCURACY ETSY FEE FORMULAS
def calculate_etsy_fees(item_price, shipping_fee, is_usd, apply_uk_vat):
    # Standard rates
    # Listing Fee: $0.20 USD converted to GBP if UK
    listing_fee = 0.20 if is_usd else 0.16 # High approximation or Etsy UK standard listing
    
    # Transaction Fee: 6.5% of total paid (listing price + shipping charged)
    total_revenue = item_price + shipping_fee
    transaction_fee = total_revenue * 0.065
    
    # Standard Payment Processing
    if is_usd:
        # Standard US: 3.0% + $0.25 (of total paid)
        processing_fee = (total_revenue * 0.03) + 0.25
    else:
        # Standard UK: 4.0% + £0.20 (of total paid)
        processing_fee = (total_revenue * 0.04) + 0.20
        
    # Standard UK VAT rules (if applied)
    # Deducts standard 20% on listing, transaction, and standard processing fees if true
    if not is_usd and apply_uk_vat:
        listing_fee_vat = listing_fee * 0.20
        transaction_fee_vat = transaction_fee * 0.20
        processing_fee_vat = processing_fee * 0.20
        
        listing_fee += listing_fee_vat
        transaction_fee += transaction_fee_vat
        processing_fee += processing_fee_vat

    total_fees = listing_fee + transaction_fee + processing_fee
    return {
        "listing": listing_fee,
        "transaction": transaction_fee,
        "processing": processing_fee,
        "total": total_fees
    }

# Pricing solver - Find recommended item listing price to achieve exact target margin algebraically
def solve_recommended_price(costs_sum, shipping_fee, is_usd, apply_uk_vat, target_m):
    # Establish VAT factor
    vat_multiplier = 1.0
    if not is_usd and apply_uk_vat:
        vat_multiplier = 1.2

    # Variable Fee Percent representing transaction and processing fee rates
    if is_usd:
        var_fee_pct = (0.065 + 0.03) * vat_multiplier  # 0.095
    else:
        var_fee_pct = (0.065 + 0.04) * vat_multiplier  # 0.105 * 1.2 = 0.126

    # Fixed fees components (listing fee + physical payment processing fixed charge)
    if is_usd:
        fixed_fees = (0.20 + 0.25) * vat_multiplier  # 0.45
    else:
        fixed_fees = (0.16 + 0.20) * vat_multiplier  # 0.432 if apply_uk_vat, else 0.36

    denominator = 1.0 - var_fee_pct - target_m
    # Prevent divide-by-zero or negative denominator mapping representing mathematically impossible margins
    if denominator <= 0.01:
        denominator = 0.01

    raw_price = ((costs_sum + fixed_fees) / denominator) - shipping_fee
    return max(0.01, raw_price)

recommended_listing_price = solve_recommended_price(gross_cost_per_item, shipping_fee=shipping_charged, is_usd=is_us, apply_uk_vat=apply_vat, target_m=target_margin)
recommended_fees = calculate_etsy_fees(recommended_listing_price, shipping_charged, is_us, apply_vat)
recommended_total_payout = (recommended_listing_price + shipping_charged) - (gross_cost_per_item + recommended_fees["total"])

# Break even listing price (0% target margin)
breakeven_listing_price = solve_recommended_price(gross_cost_per_item, shipping_fee=shipping_charged, is_usd=is_us, apply_uk_vat=apply_vat, target_m=0.0)
breakeven_fees = calculate_etsy_fees(breakeven_listing_price, shipping_charged, is_us, apply_vat)

# RIGHT SIDE OUTPUT DASH & PRICE SIMULATOR
with right_col:
    st.markdown("### 📊 Recommended Retail Parameters")
    
    # Metric Display Box
    st.markdown(f"""
    <div style="background-color: #111827; padding: 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px;">
        <span style="font-size: 11px; color:#a1a1aa; font-weight:600; text-transform: uppercase; letter-spacing: 0.1em; display:block;">Recommended Product Listing Price</span>
        <strong style="font-size: 2.5rem; color:#f59e0b; font-weight: 850; font-family: monospace; display:block; margin: 4px 0;">{format_currency(recommended_listing_price, symbol)}</strong>
        <p style="font-size: 12px; color:#10b981; margin:0; font-weight: 600;">✅ Achieves specified {target_margin*100:.0f}% Target Profit Margin</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.metric(
            label="Break-Even Price", 
            value=format_currency(breakeven_listing_price, symbol),
            help="Listing less than this amount directly guarantees transactional losses."
        )
    with c2:
        st.metric(
            label="Sum of All Production Costs", 
            value=format_currency(gross_cost_per_item, symbol),
            help="Total of raw materials, labor, shipping cost, and packaging items combined."
        )

    st.markdown("<hr style='margin: 1.5rem 0; border: 0; border-top: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

    # "WHAT IF" PRICE SLIDER & SIMULATOR
    st.markdown("### 🎚️ \"What-If\" Selling Price Simulator")
    st.markdown("Test a custom listing retail price to see immediate breakdown projection updates.")
    
    # Restrict min_value of inputs to minimum of 1.00 as requested to prevent division by zero anywhere
    sim_min_val = max(1.00, float(round(breakeven_listing_price/2.0, 1)))
    sim_max_val = max(sim_min_val + 5.0, float(round(recommended_listing_price*2.0, 1) + 20.0))
    sim_val = max(sim_min_val, float(round(recommended_listing_price, 1)))
    
    sim_price = st.slider(
        f"Simulate Customer Price Selection ({symbol})",
        min_value=sim_min_val,
        max_value=sim_max_val,
        value=sim_val,
        step=0.1
    )
    
    sim_fees = calculate_etsy_fees(sim_price, shipping_charged, is_us, apply_vat)
    sim_gross_revenue = sim_price + shipping_charged
    sim_total_expenses = gross_cost_per_item + sim_fees["total"]
    sim_net_profit = sim_gross_revenue - sim_total_expenses
    sim_margin_pct = (sim_net_profit / sim_gross_revenue) * 100.0 if sim_gross_revenue > 0 else 0.0

    # Color coded profit indicators
    status_color = "#10b981" if sim_net_profit >= 0 else "#ef4444"
    status_label = "PROFIT" if sim_net_profit >= 0 else "LOSS"
    
    st.markdown(f"""
    <div style="background-color: #0d1117; padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); text-align: center; margin-bottom: 15px;">
        <span style="font-size:10px; color:rgba(255,255,255,0.4); text-transform:uppercase; font-weight:bold;">Simulator Net Take-Home</span>
        <strong style="font-size:1.8rem; font-family: monospace; color:{status_color}; display:block;">{format_currency(sim_net_profit, symbol)}</strong>
        <span style="display:inline-block; font-size:11px; background-color:{status_color}25; color:{status_color}; font-weight:bold; border-radius:100px; padding: 2px 8px;">
            {sim_margin_pct:.1f}% NET MARGIN ({status_label})
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Where does the money go? Stacked metrics breakdown layout
    st.markdown("##### 🪙 Fee & Cost Distribution Breakdown")
    
    total_parts = total_materials_cost + total_labor_cost + (packaging_cost + actual_postage) + sim_fees["total"] + max(0.0, sim_net_profit)
    if total_parts > 0:
        mat_pct = (total_materials_cost / total_parts) * 100.0
        lab_pct = (total_labor_cost / total_parts) * 100.0
        ship_pct = ((packaging_cost + actual_postage) / total_parts) * 100.0
        fees_pct = (sim_fees["total"] / total_parts) * 100.0
        prof_pct = (max(0.0, sim_net_profit) / total_parts) * 100.0
        
        # Redesigned as a clean, stacked st.container with columns displaying st.metric cards to prevent poor mobile text wrapping/clashes
        with st.container():
            bd_col1, bd_col2 = st.columns(2)
            with bd_col1:
                st.metric(
                    label="Materials Cost",
                    value=format_currency(total_materials_cost, symbol),
                    delta=f"{mat_pct:.1f}% allotment",
                    delta_color="off"
                )
                st.metric(
                    label="Labor Support",
                    value=format_currency(total_labor_cost, symbol),
                    delta=f"{lab_pct:.1f}% allotment",
                    delta_color="off"
                )
                st.metric(
                    label="Shipping & Packaging",
                    value=format_currency(packaging_cost + actual_postage, symbol),
                    delta=f"{ship_pct:.1f}% allotment",
                    delta_color="off"
                )
            with bd_col2:
                st.metric(
                    label="Etsy Platform Fees",
                    value=format_currency(sim_fees["total"], symbol),
                    delta=f"{fees_pct:.1f}% allotment",
                    delta_color="inverse"
                )
                st.metric(
                    label="Take-Home Profit",
                    value=format_currency(max(0.0, sim_net_profit), symbol),
                    delta=f"{prof_pct:.1f}% allotment",
                    delta_color="normal"
                )

    # Fees itemized breakdown
    with st.expander("📝 Detailed Etsy Transaction Fees Breakdown", expanded=False):
        fee_tbl = pd.DataFrame({
            "Fee Component": ["Listing Fee (lasts 4 months)", "Transaction Fee (6.5% of order sum)", "Standard Payment Processing", "Total Platform Deductions"],
            "Standard Assessment": [
                "Fixed flat fee per item" if is_us else "Approx equivalent including standard rate",
                "Assessed on Listing Price + Shipping Charged",
                "US standard: 3.0% + $0.25" if is_us else "UK standard: 4.0% + £0.20",
                "Combined deductions"
            ],
            "Projected cost": [
                format_currency(sim_fees['listing'], symbol),
                format_currency(sim_fees['transaction'], symbol),
                format_currency(sim_fees['processing'], symbol),
                format_currency(sim_fees['total'], symbol)
            ]
        })
        st.table(fee_tbl)
        if not is_us and apply_vat:
            st.caption("ℹ️ Includes HMRC 20% VAT applied on top of internal Etsy fees.")

st.markdown("<hr style='margin: 2rem 0; border: 0; border-top: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

# CRAFTER ADVICE SECTION
st.markdown("### 🌟 Professional Etsy Crafter Strategy Advice")
sc1, sc2 = st.columns(2)
with sc1:
    st.markdown("""
    **📦 Shipping Charges vs. Listings:**
    Unless you offer fully-subsidized 'Free Shipping' options, the buyer always pays `Shipping Charged`. 
    Remember: Etsy applies their transaction fees on both the **listing item price AND the shipping fee**. 
    Hence, charging $5 postage + $15 item cost produces exactly the same $1.30 Etsy transaction fee as listing the item at $20 with free postage.
    """)
with sc2:
    st.markdown("""
    **⏱️ Internalized Labor Valuation:**
    Never overlook your physical packing, post-office delivery, or customized wrapping time! 
    Always record your true average creation time per item (`Time Spent per Item` slider), 
    and pay yourself a premium, fair hourly wage. If you let target profit default to cover your wages, 
    your craft brand won't build durable enterprise value!
    """)
