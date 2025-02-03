import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.seasonal import seasonal_decompose
from pymongo import MongoClient
from scipy.signal import savgol_filter

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")  # Ensure MongoDB is running locally
db = client["ProjectStreamlit"]  # Use your database name
collection = db["p"]  # Use your collection name

# Title and description
st.title("Time Series Forecasting with Interactive Graphs")
st.write("""
On this page, you can:
1. View the **forecast of future average prices** per supermarket.
2. Analyze **daily price trends** to determine the cheapest or most expensive shopping days.
""")

# Fetch available supermarkets and categories from MongoDB
supermarkets = collection.distinct("supermarket")
categories = collection.distinct("category")

col1, col2 = st.columns(2)

with col1:
    selected_supermarket = st.selectbox("Pick a supermarket", supermarkets)

with col2:
    selected_category = st.selectbox("Select a category", ["All"] + categories)

# Build MongoDB query
query = {"supermarket": selected_supermarket}
if selected_category != "All":
    query["category"] = selected_category

# Fetch data from MongoDB
cursor = collection.find(query, {"_id": 0, "supermarket": 1, "prices_(€)": 1, "date": 1})
data = pd.DataFrame(list(cursor))

if not data.empty:
    # Convert 'date' column to datetime
    data["date"] = pd.to_datetime(data["date"], format="%Y%m%d", errors="coerce")
    data.set_index("date", inplace=True)
    
    # Perform seasonal decomposition
    result = seasonal_decompose(data["prices_(€)"], model="multiplicative", period=7)
    trend = result.trend.dropna()

    # Apply Savitzky-Golay filter for smooth trend
    smoothed_trend = savgol_filter(trend, window_length=21, polyorder=3, mode='nearest')

    # --- 📈 Interactive Trend Plot Using Plotly ---
    trend_fig = go.Figure()
    trend_fig.add_trace(go.Scatter(
        x=trend.index, y=trend, mode='lines', name="Original Trend",
        line=dict(color="lightgray", dash="dash")
    ))
    trend_fig.add_trace(go.Scatter(
        x=trend.index, y=smoothed_trend, mode='lines', name="Smoothed Trend",
        line=dict(color="blue", width=3)
    ))
    trend_fig.update_layout(
        title="Smoothed Trend (Savitzky-Golay Filter)",
        xaxis_title="Date", yaxis_title="Price (€)",
        template="plotly_dark", height=500
    )
    st.plotly_chart(trend_fig)

    # --- 📊 Interactive Weekly Price Line Graph ---
    data['day_of_week'] = data.index.dayofweek
    weekly_data = data.groupby('day_of_week')['prices_(€)'].mean()
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_data.index = days_order

    week_fig = go.Figure()
    week_fig.add_trace(go.Scatter(
        x=weekly_data.index,
        y=weekly_data.values,
        mode='lines+markers',
        line=dict(color='blue', width=2),
        marker=dict(size=8),
        name='Average Price'
    ))
    week_fig.update_layout(
        title="Average Price by Day of Week",
        xaxis_title="Day of the Week",
        yaxis_title="Average Price (€)",
        template="plotly_dark",
        xaxis={'categoryorder': 'array', 'categoryarray': days_order},
        height=500
    )
    st.plotly_chart(week_fig)

else:
    st.warning("No data available for the selected supermarket and category.")