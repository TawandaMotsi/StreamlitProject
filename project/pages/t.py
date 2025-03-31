import streamlit as st

# Application Title
st.title("Welcome to Irish Supermarket Price Analyser! 🛒📈")

# Sidebar Navigation
st.sidebar.title("Navigate the Site")
page = st.sidebar.radio("Select a section:", [
    "About Me",
    "Requirements",
    "Process Explanation",
    "Data Quality",
    "Daily Product Analysis",
    "Pricing Psychology",
    "Time Series Forecasting",
    "Weekly Inflation",
    "Product Price Comparison",
    "Recommender System",
    "All Issue Log"
])

# Content Rendering Based on Selection
st.subheader(f"{page}")

if page == "About Me":
    st.write("Discover why this site was created.")

elif page == "Requirements":
    st.write("Understand what the project's technical and business requirements are.")

elif page == "Process Explanation":
    st.write("Dive into the methodology for collecting and presenting pricing data.")

elif page == "Data Quality":
    st.write("Learn about the commitment to accuracy, reliability, and timeliness in the data provided.")

elif page == "Daily Product Analysis":
    st.write("Deep dive into daily pricing analysis for branded and own-brand products.")

elif page == "Pricing Psychology":
    st.write("Gain insights into how different supermarkets use pricing behavior to influence consumers.")

elif page == "Time Series Forecasting":
    st.write("Use historical data to predict future price movements or view the cheapest day to shop!")

elif page == "Weekly Inflation":
    st.write("Track inflation trends on a weekly basis to stay informed.")

elif page == "Product Price Comparison":
    st.write("Compare prices across different supermarkets to find the best deals.")

elif page == "Recommender System":
    st.write("Get personalized product recommendations based on your shopping habits.")

elif page == "All Issue Log":
    st.write("Contains a sample list of issues encountered whilst creating this project.")
