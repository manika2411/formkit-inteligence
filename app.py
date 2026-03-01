import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="FormKit Intelligence Platform", layout="wide")

st.title("🏗️ FormKit Intelligence Platform – Prototype")
st.markdown("AI-Driven Portfolio-Aware Formwork Kitting Optimizer")

uploaded_file = st.file_uploader("Upload Project CSV", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    required_cols = ["Project", "Floor", "ElementType", "Area", "Week"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"CSV must contain column: {col}")
            st.stop()

    # -----------------------------
    # CONFIGURABLE PARAMETERS
    # -----------------------------
    st.sidebar.header("⚙️ Cost & Model Parameters")

    panel_coverage = st.sidebar.number_input("Panel Coverage (m² per panel)", value=5.0)
    panel_cost = st.sidebar.number_input("Panel Cost (₹ per panel)", value=35000)
    holding_rate = st.sidebar.slider("Weekly Holding Cost (%)", 0.0, 10.0, 2.0)

    # -----------------------------
    # AUTO BOQ GENERATION
    # -----------------------------
    df["Panels"] = df["Area"] / panel_coverage

    st.subheader("📋 Auto-Generated BoQ")
    st.dataframe(df)

    # -----------------------------
    # BASELINE MODEL
    # -----------------------------
    # Independent procurement per project
    baseline_panels = df.groupby("Project")["Panels"].sum().sum()

    # -----------------------------
    # OPTIMIZED PORTFOLIO MODEL
    # -----------------------------
    weekly_demand = df.groupby("Week")["Panels"].sum()
    optimized_panels = weekly_demand.max()

    # -----------------------------
    # HEALTH AWARE ADJUSTMENT
    # -----------------------------
    st.subheader("🔧 Panel Health Simulation")
    health = st.slider("Average Panel Health (%)", 40, 100, 80)

    if health < 60:
        optimized_panels *= 1.15
    elif health < 75:
        optimized_panels *= 1.05

    baseline_panels = int(baseline_panels)
    optimized_panels = int(optimized_panels)

    # -----------------------------
    # COST CALCULATIONS
    # -----------------------------
    baseline_cost = baseline_panels * panel_cost
    optimized_cost = optimized_panels * panel_cost

    # Holding cost impact
    baseline_holding = baseline_cost * (holding_rate / 100)
    optimized_holding = optimized_cost * (holding_rate / 100)

    total_baseline = baseline_cost + baseline_holding
    total_optimized = optimized_cost + optimized_holding

    savings = total_baseline - total_optimized

    reduction_percent = ((baseline_panels - optimized_panels) / baseline_panels) * 100

    # -----------------------------
    # RESULTS DISPLAY
    # -----------------------------
    st.subheader("📊 Optimization Results")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Baseline Panels Required", baseline_panels)
        st.metric("Baseline Procurement Cost", f"₹{baseline_cost:,}")
        st.metric("Baseline Holding Cost (Weekly)", f"₹{baseline_holding:,.0f}")

    with col2:
        st.metric("Optimized Panels Required", optimized_panels)
        st.metric("Optimized Procurement Cost", f"₹{optimized_cost:,}")
        st.metric("Optimized Holding Cost (Weekly)", f"₹{optimized_holding:,.0f}")

    if savings > 0:
        st.success(f"💰 Total Estimated Savings (Procurement + Weekly Holding): ₹{savings:,.0f}")
        st.info(f"📉 Inventory Reduction: {reduction_percent:.1f}%")
    else:
        st.warning("No savings under current schedule.")

    # -----------------------------
    # WORKING CAPITAL IMPACT
    # -----------------------------
    st.subheader("💼 Working Capital Impact")

    working_capital_reduction = baseline_cost - optimized_cost

    st.write(f"Reduction in Working Capital Locked: ₹{working_capital_reduction:,.0f}")

    # -----------------------------
    # WEEKLY DEMAND GRAPH
    # -----------------------------
    st.subheader("📈 Weekly Panel Demand (Portfolio View)")

    fig, ax = plt.subplots()
    ax.plot(weekly_demand.index, weekly_demand.values, marker="o")
    ax.set_xlabel("Week")
    ax.set_ylabel("Panels Required")
    ax.set_title("Weekly Portfolio Panel Demand")
    st.pyplot(fig)

else:
    st.info("Please upload a CSV file to begin.")