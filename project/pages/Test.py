import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns

def load_data():
    # Load dataset (Ensure CSV has 'Product Name', 'Price', 'Supermarket')
    return pd.read_csv('price_data.csv')

def preprocess_price(price):
    # Extract the decimal part (pence value)
    return round(price % 1, 2) * 100

def match_product(product_name, data):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(data['Product Name'])
    query_vector = vectorizer.transform([product_name])
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    data['Similarity'] = similarities
    return data.sort_values(by='Similarity', ascending=False).head(5)

def price_psychology_analysis(data):
    data['Pence Value'] = data['Price'].apply(preprocess_price)
    plt.figure(figsize=(10, 5))
    sns.histplot(data['Pence Value'], bins=20, kde=True)
    plt.xlabel('Pence Value (XX in £YY.XX)')
    plt.ylabel('Frequency')
    plt.title('Price Psychology Analysis')
    st.pyplot(plt)

def main():
    st.title("Supermarket Price Comparison & Analysis")
    data = load_data()
    
    tab1, tab2 = st.tabs(["Price Comparison", "Price Psychology Analysis"])
    
    with tab1:
        st.subheader("Find Similar Products Across Supermarkets")
        product_name = st.text_input("Enter Product Name:")
        if st.button("Compare Prices"):
            results = match_product(product_name, data)
            st.write(results[['Supermarket', 'Product Name', 'Price']])
    
    with tab2:
        st.subheader("Psychological Pricing Patterns")
        if st.button("Analyze Price Endings"):
            price_psychology_analysis(data)

if __name__ == "__main__":
    main()
 