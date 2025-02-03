import streamlit as st
import pandas as pd
import os

# Streamlit App Title
st.title("Data Quality Analysis")

# Description
st.write("""
This section focuses on the data quality metrics during web scraping and data cleaning processes.
""")

# List of available CSV files
csv_files = [
    "20241122.csv",
    "20241123.csv",
    "20241124.csv"
]

# Dropdown for file selection
selected_file = st.selectbox("Select a CSV file:", csv_files)

# Path to the folder where CSV files are stored
csv_folder_path = "/Users/tawandamotsi/Downloads/ProjectStreamlit/project/pages/csvFiles/"

# Load the selected CSV file
file_path = os.path.join(csv_folder_path, selected_file)
df = pd.read_csv(file_path)

# Check if 'Date' column exists
if "Date" in df.columns:
    # Select a date
    selected_date = st.selectbox("Select a date:", df["Date"].unique(), key="date_selector")
    filtered_data = df[df["Date"] == selected_date]
else:
    st.error("The dataset does not contain a 'Date' column.")
    filtered_data = df

# Display data quality description
st.write("""
This table shows the data quality during the web scraping and data cleaning processes:

1. **Boxes**: The number of product boxes that were web-scraped.
2. **Names**: The number of names that were web-scraped.
3. **Extra Boxes**: 'Boxes' minus 'Names'. Shows if any boxes were web-scraped but no other data was obtained for them.
4. **Out of Stock**: Items with a name but no price. This is because it's removed for out-of-stock items.
5. **Unique Names**: Number of unique names web-scraped.
6. **Final Count**: Final number of products with all data available.
7. **Names Missing**: Difference between unique names and final number of products available.
""")

# Select supermarkets
if "Supermarket" in df.columns:
    supermarkets = st.multiselect(
        "Select supermarkets:",
        options=df["Supermarket"].unique(),
        default=df["Supermarket"].unique()
    )
    filtered_data = filtered_data[filtered_data["Supermarket"].isin(supermarkets)]
else:
    st.error("The dataset does not contain a 'Supermarket' column.")

# Display filtered data for Web Scraper Data Quality
st.write("### Web Scraper Data Quality Table")
st.dataframe(filtered_data)

# Final Dataset Data Quality Section
st.write("### Final Dataset Data Quality")
st.write("""
This section checks for null values in the final documents.
""")

# Check for null values in the filtered dataset
null_values = filtered_data.isnull().sum().to_frame(name="Null Count").reset_index()
null_values.rename(columns={"index": "Column"}, inplace=True)

# Display null values table
st.write("Null Values in Final Dataset")
st.table(null_values)
