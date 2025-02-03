from prophet import Prophet
import pandas as pd
import numpy as np
from pymongo import MongoClient
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")  # Ensure MongoDB is running locally
db = client["ProjectStreamlit"]  # Use your database name
collection = db["p"]  # Use your collection name

# Streamlit UI
st.title("Price Prediction Tool")
st.subheader("Objective")
st.write("""
This script predicts the price of a product for the next 3 days using a time series model.
It fetches data from MongoDB and applies Facebook Prophet for forecasting.
""")

def preprocess_text(text):
    """Preprocess text by converting to lowercase and removing extra spaces"""
    if isinstance(text, str):
        return ' '.join(text.lower().split())
    return ''

def calculate_similarity(keyword, product_names):
    """Calculate cosine similarity between the keyword and product names"""
    try:
        processed_keyword = preprocess_text(keyword)
        processed_names = [preprocess_text(name) for name in product_names]

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(processed_names)
        keyword_vector = vectorizer.transform([processed_keyword])

        similarity_scores = cosine_similarity(keyword_vector, tfidf_matrix).flatten()
        similarity_scores = similarity_scores * 100  # Convert to percentage

        return similarity_scores
    except Exception as e:
        st.error(f"Error calculating similarity: {e}")
        return np.zeros(len(product_names))  # Return an array of zeros if there's an error

# User input for product selection
keyword = st.text_input("Enter a keyword", value="chicken dippers")
min_similarity = st.slider("Minimum Similarity Score", 0, 100, 50)

# Fetch available dates and categories from MongoDB
available_dates = collection.distinct("date")  # Dates are stored as int32 in MongoDB
available_categories = collection.distinct("category")  # Fetch distinct categories

if available_dates:
    available_dates = [int(date) for date in available_dates if isinstance(date, (int, str))]
    available_dates = sorted(available_dates, reverse=True)
    date_options = [str(date) for date in available_dates]
    selected_date_str = st.selectbox("Select a date", date_options)
    selected_date = int(selected_date_str)
else:
    st.error("No date data found in the database.")
    selected_date = None

if available_categories:
    category_options = ["All"] + available_categories
    selected_category = st.selectbox("Select a category", category_options)
else:
    st.error("No category data found in the database.")
    selected_category = "All"

if selected_date:
    query = {"date": selected_date}
    if selected_category != "All":
        query["category"] = selected_category

    try:
        cursor = collection.find(query)
        data = list(cursor)

        if not data:
            st.warning(f"No data found for the selected date and category: {selected_date}, {selected_category}")
        else:
            # Create DataFrame
            df = pd.DataFrame(data)

            if not df.empty:
                required_columns = ["names", "supermarket", "prices_(€)", "prices_unit_(€)", "unit", "category", "own_brand", "date"]
                if all(col in df.columns for col in required_columns):
                    similarity_scores = calculate_similarity(keyword, df["names"])
                    df["similarity"] = similarity_scores

                    # Filter by similarity
                    df = df[df["similarity"] >= min_similarity]

                    if not df.empty:
                        df["similarity"] = df["similarity"].round(2)
                        df = df.sort_values(by="similarity", ascending=False)

                        st.write(f"Found {len(df)} matching products:")

                        # Prepare data for forecasting
                        product = df.iloc[0]  # Take the top result
                        product_prices = df[["date", "prices_(€)"]]  # Use the product prices for prediction
                        product_prices = product_prices.rename(columns={"date": "ds", "prices_(€)": "y"})  # Prophet format

                        # Clean the data (remove NaNs)
                        product_prices = product_prices.dropna(subset=["ds", "y"])

                        # Check if there are enough rows for forecasting
                        if len(product_prices) < 2:
                            st.error("Not enough valid data for forecasting. At least two rows are required.")
                        else:
                            try:
                                # Fit Prophet model
                                model = Prophet()
                                model.fit(product_prices)

                                # Make future predictions
                                future = model.make_future_dataframe(product_prices, periods=3)  # Predict the next 3 days
                                forecast = model.predict(future)

                                # Display forecast results
                                st.write("Predicted Prices for the Next 3 Days:")

                                forecast = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]  # Display only the relevant columns
                                forecast["ds"] = forecast["ds"].dt.strftime('%Y-%m-%d')  # Format date

                                st.dataframe(forecast)

                                # Optionally, plot the forecast
                                fig = model.plot(forecast)
                                st.pyplot(fig)

                            except ValueError as e:
                                st.error(f"Error fitting the model: {e}")

                    else:
                        st.warning("No products match the specified criteria.")
                else:
                    st.error("The data does not contain the required columns.")
            else:
                st.warning("The DataFrame is empty after loading data from MongoDB.")
    except Exception as e:
        st.error(f"Error querying MongoDB: {e}")
