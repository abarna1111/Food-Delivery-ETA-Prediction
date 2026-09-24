import streamlit as st
import pandas as pd
import joblib

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Food Delivery ETA Dashboard",
    page_icon="🍔",
    layout="wide"
)

# -----------------------------
# Load Model and Data
# -----------------------------
model = joblib.load("food_delivery_eta_model.pkl")
features = joblib.load("model_features.pkl")

df = pd.read_csv("live_orders.csv")

# -----------------------------
# Title
# -----------------------------
st.title("🍔 Food Delivery ETA Prediction Dashboard")
st.write("Real-time simulated food delivery order monitoring and ETA prediction")
if st.button("🔄 Refresh Dashboard"):
    st.rerun()
st.divider()

# -----------------------------
# KPI Calculations
# -----------------------------
total_orders = len(df)

active_orders = len(
    df[df["status"].isin(["Preparing", "Picked Up", "On the Way"])]
)

delivered_orders = len(
    df[df["status"] == "Delivered"]
)

average_eta = df["predicted_eta_min"].mean()

# -----------------------------
# KPI Display
# -----------------------------
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(
    "Total Orders",
    total_orders
)

col2.metric(
    "Active Orders",
    active_orders
)

col3.metric(
    "Delivered Orders",
    delivered_orders
)

col4.metric(
    "Average ETA",
    f"{average_eta:.1f} min"
)

high_eta_count = len(
    df[df["predicted_eta_min"] >= 30]
)

delay_percentage = (
    high_eta_count / total_orders * 100
    if total_orders > 0 else 0
)

col5.metric(
    "High ETA %",
    f"{delay_percentage:.1f}%"
)
st.divider()

# -----------------------------
# Live Orders Table
# -----------------------------
st.subheader("📦 Live Orders")

display_columns = [
    "order_id",
    "first_mile_distance",
    "last_mile_distance",
    "predicted_eta_min",
    "status"
]

st.dataframe(
    df[display_columns],
    use_container_width=True,
    hide_index=True
)

st.divider()
# -----------------------------
# ETA Distribution
# -----------------------------
st.subheader("📊 Predicted ETA Distribution")

eta_bins = pd.cut(
    df["predicted_eta_min"],
    bins=10
)

eta_distribution = (
    eta_bins
    .value_counts()
    .sort_index()
)

eta_distribution.index = [
    f"{interval.left:.0f}-{interval.right:.0f} min"
    for interval in eta_distribution.index
]

st.bar_chart(
    eta_distribution,
    use_container_width=True
)

st.divider()
st.subheader("📦 Order Status Summary")

status_counts = df["status"].value_counts()

st.bar_chart(
    status_counts,
    use_container_width=True
)

st.divider()
# -----------------------------
# Distance vs Predicted ETA
# -----------------------------
st.subheader("📍 Distance vs Predicted ETA")

st.scatter_chart(
    df,
    x="last_mile_distance",
    y="predicted_eta_min",
    use_container_width=True
)

st.divider()
# -----------------------------
# High ETA Orders
# -----------------------------
st.subheader("⚠️ High ETA Orders")

high_eta_orders = df[
    df["predicted_eta_min"] >= 30
]

if len(high_eta_orders) > 0:
    st.dataframe(
        high_eta_orders[
            [
                "order_id",
                "last_mile_distance",
                "predicted_eta_min",
                "status"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("No high ETA orders currently.")

st.divider()
# -----------------------------
# ETA Prediction Section
# -----------------------------
st.subheader("🔮 Predict Delivery ETA")

col1, col2 = st.columns(2)

with col1:
    first_mile = st.number_input(
        "First-Mile Distance (km)",
        min_value=0.0,
        value=2.0
    )

    last_mile = st.number_input(
        "Last-Mile Distance (km)",
        min_value=0.0,
        value=3.0
    )

    alloted_orders = st.number_input(
        "Alloted Orders",
        min_value=0,
        value=5
    )

    delivered = st.number_input(
        "Delivered Orders",
        min_value=0,
        value=100
    )

    undelivered = st.number_input(
        "Undelivered Orders",
        min_value=0,
        value=2
    )

    lifetime_orders = st.number_input(
        "Lifetime Order Count",
        min_value=0,
        value=150
    )

with col2:
    session_time = st.number_input(
        "Session Time",
        min_value=0,
        value=300
    )

    reassigned = st.selectbox(
        "Reassigned Order",
        [0, 1]
    )

    order_hour = st.slider(
        "Order Hour",
        min_value=0,
        max_value=23,
        value=19
    )

    day_of_week = st.slider(
        "Day of Week",
        min_value=0,
        max_value=6,
        value=2
    )

    is_weekend = st.selectbox(
        "Weekend",
        [0, 1]
    )

    is_peak = st.selectbox(
        "Peak Hour",
        [0, 1]
    )

# -----------------------------
# Prediction
# -----------------------------
if st.button("Predict ETA"):

    input_data = pd.DataFrame([{
        "first_mile_distance": first_mile,
        "last_mile_distance": last_mile,
        "alloted_orders": alloted_orders,
        "delivered_orders": delivered,
        "undelivered_orders": undelivered,
        "lifetime_order_count": lifetime_orders,
        "session_time": session_time,
        "reassigned_order": reassigned,
        "order_hour": order_hour,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "is_peak_hour": is_peak
    }])

    prediction = model.predict(input_data[features])[0]

    st.success(
        f"Estimated Delivery Time: {prediction:.2f} minutes"
    )

st.divider()

st.caption(
    "Note: This dashboard uses simulated live orders and a model trained on historical delivery data."
)