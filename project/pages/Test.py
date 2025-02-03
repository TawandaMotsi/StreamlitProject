from pymongo import MongoClient
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")  # Ensure MongoDB is running locally
db = client["ProjectStreamlit"]  # Use your database name
collection = db["p"]  # Use your collection name

# Streamlit UI
st.title("Price Comparison Tool")
st.subheader("Objective")
st.write("""
This script allows users to search for any item available in all supermarkets on any date. 
The algorithm uses an enhanced TF-IDF matrix to calculate precise cosine similarity scores between the item names and the search keyword.
""")

st.write("""
The table contains:
1. Similarity score between the keyword and items
2. Name of the supermarket
3. The price of the item
4. The price per unit
5. Unit measurement
6. Category of the item
7. Whether the item is an own-brand good or not
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
        similarity_scores = similarity_scores * 100

        return similarity_scores
    except Exception as e:
        st.error(f"Error calculating similarity: {e}")
        return np.zeros(len(product_names))

# User inputs
keyword = st.text_input("Enter a keyword", value="chicken dippers")
min_similarity = st.slider("Minimum Similarity Score", 0, 100, 50)

# Fetch available dates from MongoDB
available_dates = collection.distinct("date")  # Dates are stored as int32 in MongoDB

if available_dates:
    # Convert all dates to integers (handle mixed types)
    available_dates = [int(date) for date in available_dates if isinstance(date, (int, str))]
    available_dates = sorted(available_dates, reverse=True)  # Sort dates in descending order
    date_options = [str(date) for date in available_dates]  # Convert dates to strings for display
    selected_date_str = st.selectbox("Select a date", date_options)  # Display date options in selectbox
    selected_date = int(selected_date_str)  # Convert selected date back to int
else:
    st.error("No date data found in the database.")
    selected_date = None


if selected_date:
    query = {"date": selected_date}  # Use the selected date as int32 in the query
    try:
        cursor = collection.find(query)
        data = list(cursor)

        if not data:
            st.warning(f"No data found for the selected date: {selected_date}")
        else:
            # Create DataFrame
            df = pd.DataFrame(data)

            if not df.empty:
                # Check for required columns
                required_columns = ["names", "supermarket", "prices_(€)", "prices_unit_(€)", "unit", "category", "own_brand", "date"]
                if all(col in df.columns for col in required_columns):
                    similarity_scores = calculate_similarity(keyword, df["names"])
                    df["similarity"] = similarity_scores

                    # Filter by similarity
                    df = df[df["similarity"] >= min_similarity]

                    if not df.empty:
                        df["similarity"] = df["similarity"].round(2)
                        df = df.sort_values(by="similarity", ascending=False)

                        # Display results
                        st.write(f"Found {len(df)} matching products:")
                        display_columns = [
                            "similarity", "supermarket", "prices_(€)", "prices_unit_(€)", "unit", 
                            "names", "date", "category", "own_brand"
                        ]
                        st.dataframe(
                            df[display_columns],
                            height=400,
                            hide_index=True
                        )

                        # Summary statistics
                        st.write(f"Minimum price: €{df['prices_(€)'].min():.2f}")
                        st.write(f"Average price: €{df['prices_(€)'].mean():.2f}")
                        st.write(f"Price range: €{df['prices_(€)'].min():.2f} - €{df['prices_(€)'].max():.2f}")
                    else:
                        st.warning("No products match the specified criteria.")
                else:
                    st.error("The data does not contain the required columns.")
            else:
                st.warning("The DataFrame is empty after loading data from MongoDB.")
    except Exception as e:
        st.error(f"Error querying MongoDB: {e}")
