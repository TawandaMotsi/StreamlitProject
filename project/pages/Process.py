import streamlit as st
st.set_page_config(layout="wide")

def main():
    st.title("The Process")
    st.write("This page will explain, in detail, the end-to-end process for the webscraping, data processing and data analysis of the supermarket data.")

    st.header("Website Data")
    st.write("The product data is webscraped directly from the supermarkets websites for Aldi, Lidl and Tesco.")
    st.write("The main Python libraries used are Pandas, Selenium and Beautiful Soup")

    st.markdown("""
    The information web-scraped is:
    1. Product Box  
    2. Product Name  
    3. Product Price  
    4. Product Price per Unit
    """)

    st.header("Price Comparison")

    with st.expander("Code: Full Price Comparison"):
        st.code("""
from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def preprocess_text(text):
    if isinstance(text, str):
        return ' '.join(text.lower().split())
    return ''

def calculate_similarity(keyword, product_names):
    try:
        processed_keyword = preprocess_text(keyword)
        processed_names = [preprocess_text(name) for name in product_names]

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(processed_names)
        keyword_vector = vectorizer.transform([processed_keyword])

        similarity_scores = cosine_similarity(keyword_vector, tfidf_matrix).flatten() * 100
        return similarity_scores
    except Exception as e:
        st.error(f"Error calculating similarity: {e}")
        return np.zeros(len(product_names))

client = MongoClient("mongodb://localhost:27017/")
db = client["ProjectStreamlit"]
collection = db["p"]

keyword = st.text_input("Enter a keyword", value="chicken dippers")
min_similarity = st.slider("Minimum Similarity Score", 0, 100, 50)

available_dates = collection.distinct("date")
available_categories = collection.distinct("category")

if available_dates:
    available_dates = [int(date) for date in available_dates if isinstance(date, (int, str))]
    available_dates = sorted(available_dates, reverse=True)
    selected_date_str = st.selectbox("Select a date", [str(date) for date in available_dates])
    selected_date = int(selected_date_str)
else:
    st.error("No date data found in the database.")
    selected_date = None

if available_categories:
    selected_category = st.selectbox("Select a category", ["All"] + available_categories)
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
            df = pd.DataFrame(data)
            required_columns = ["names", "supermarket", "prices_(€)", "prices_unit_(€)", "unit", "category", "own_brand", "date"]

            if not df.empty and all(col in df.columns for col in required_columns):
                similarity_scores = calculate_similarity(keyword, df["names"])
                df["similarity"] = similarity_scores
                df = df[df["similarity"] >= min_similarity]

                if not df.empty:
                    df["similarity"] = df["similarity"].round(2)
                    df = df.sort_values(by="similarity", ascending=False)

                    st.write(f"Found {len(df)} matching products:")
                    display_columns = ["similarity", "supermarket", "prices_(€)", "prices_unit_(€)", "unit", "names", "date", "category", "own_brand"]
                    st.dataframe(df[display_columns], height=400, hide_index=True)

                    st.write(f"Minimum price: €{df['prices_(€)'].min():.2f}")
                    st.write(f"Average price: €{df['prices_(€)'].mean():.2f}")
                    st.write(f"Price range: €{df['prices_(€)'].min():.2f} - €{df['prices_(€)'].max():.2f}")
                else:
                    st.warning("No products match the specified criteria.")
            else:
                st.error("The data does not contain the required columns.")
    except Exception as e:
        st.error(f"Error querying MongoDB: {e}")
        """, language="python")
        
    st.header("TF-IDF Vectorization (Term Frequency-Inverse Document Frequency) Calculation")
    with st.expander("Code: Tfidf Matrix Calculation Only"):
        st.code("""
def calculate_similarity(keyword, product_names):
    """Calculate cosine similarity between the keyword and product names"""
    try:
        # Preprocess the input keyword (e.g., lowercase, remove punctuation, etc.)
        processed_keyword = preprocess_text(keyword)

        # Preprocess each product name in the list
        processed_names = [preprocess_text(name) for name in product_names]

        # Create a TF-IDF Vectorizer instance
        # This will convert the text into numerical feature vectors
        vectorizer = TfidfVectorizer()

        # Fit the vectorizer on the product names and transform them into TF-IDF vectors
        tfidf_matrix = vectorizer.fit_transform(processed_names)

        # Transform the processed keyword into a TF-IDF vector using the same vocabulary
        keyword_vector = vectorizer.transform([processed_keyword])

        # Compute the cosine similarity between the keyword vector and each product name vector
        similarity_scores = cosine_similarity(keyword_vector, tfidf_matrix).flatten()

        # Convert the similarity scores to percentages (0–100%)
        similarity_scores = similarity_scores * 100

        # Return the similarity scores for each product name
        return similarity_scores

    except Exception as e:
        # If any error occurs, show the error using Streamlit and return zeros for all product names
        st.error(f"Error calculating similarity: {e}")
        return np.zeros(len(product_names))  # Return a list of zeros with the same length as product_names

""", language="python")

if __name__ == "__main__":
    main()
