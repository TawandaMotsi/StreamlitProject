import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.subplots as sp
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["ProjectStreamlit"]
collection = db["p"]

# Set page configuration
st.set_page_config(
    page_title="Pricing Psychology",
    page_icon="🧠",
    layout="wide"
)

def main():
    """
    Modified version that uses MongoDB instead of local files
    """
    # Fetch available dates and categories from MongoDB
    dates = sorted(collection.distinct("date"), reverse=True)
    categories = sorted(collection.distinct("category"))
    supermarkets = sorted(collection.distinct("supermarket"))

    st.header('Pricing Psychology')
    st.write('Analyse potential psychological pricing strategies across supermarkets')
    
    # User inputs
    selected_date = st.selectbox('Select the date', dates)
    selected_categories = st.multiselect('Select Categories', categories, default=categories)
    
    fig = price_psychology_histogram(selected_date, selected_categories, supermarkets)
    st.plotly_chart(fig, use_container_width=True)

def price_psychology_histogram(date, categories, supermarkets):
    """
    Create histograms from MongoDB data
    """
    colours = ['blue', 'orange', 'green', 'red', 'purple']
    histograms = []

    for supermarket, colour in zip(supermarkets, colours):
        # Query MongoDB for data
        query = {
            "date": date,
            "supermarket": supermarket,
            "category": {"$in": categories}
        }
        projection = {"_id": 0, "prices_(€)": 1, "category": 1}
        
        df = pd.DataFrame(list(collection.find(query, projection)))
        
        if not df.empty:
            # Process prices
            df['price_ending'] = df['prices_(€)'].astype(str).str.split('.').str[-1]
            df['price_ending'] = df['price_ending'].str.ljust(2, '0').str[:2]
            df['price_ending'] = pd.to_numeric(df['price_ending'], errors='coerce')
            
            # Create price ranges
            bins = list(range(0, 100, 10))
            labels = [f"{i}-{i+9}" for i in bins[:-1]]  # Adjust labels to be one less than the number of bins
            df['range'] = pd.cut(df['price_ending'], bins=bins, right=False, labels=labels)
            
            hist_data = df['range'].value_counts().sort_index()
            histograms.append((supermarket, colour, hist_data))

    # Create subplots
    fig = sp.make_subplots(
        rows=len(histograms), 
        cols=1,
        subplot_titles=[f'{supermarket} - {date}' for supermarket, _, _ in histograms]
    )

    for idx, (supermarket, colour, hist_data) in enumerate(histograms):
        fig.add_trace(
            go.Bar(
                x=hist_data.index,
                y=hist_data.values,
                marker_color=colour,
                name=supermarket
            ),
            row=idx+1,
            col=1
        )

    fig.update_layout(
        height=300*len(histograms),
        title_text=f"Price Ending Distribution - {date}",
        showlegend=False,
        margin=dict(t=100, b=100)
    )
    
    return fig

if __name__ == "__main__":
    main()
