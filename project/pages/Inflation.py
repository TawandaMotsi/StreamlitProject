import pandas as pd
import streamlit as st
import plotly.express as px
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["ProjectStreamlit"]
collection = db["p"]

# Set page configuration
st.set_page_config(
    page_title="Weekly Inflation",
    page_icon="📈",
    layout="wide"
)

def main():
    """
    Modified version that connects to MongoDB instead of local files
    """
    # Fetch available supermarkets from MongoDB
    supermarkets = collection.distinct("supermarket")
    
    st.header('📊 Weekly Price Changes')
    st.write("""These metrics display the average price over the week for each category 
    and whether they have increased or decreased on average.""")
    
    st.subheader('Average Price Changes')
    supermarket = st.selectbox('Pick a Supermarket', supermarkets)

    (categories, final_prices, final_percentage_changes, total_price_change, 
     total_price_change_percentage, grouped_data) = create_price_metrics(supermarket)

    # Display metrics
    st.metric(label="Total Price Change", value=f"€{total_price_change:.2f}",
              delta=f"{total_price_change_percentage:.2f}%")
    
    # Create columns dynamically based on number of categories
    cols = st.columns(3)  # 3 columns per row
    for idx, category in enumerate(categories):
        with cols[idx % 3]:
            st.metric(category, f'€{final_prices[category]:.2f}', 
                      f'{final_percentage_changes[category]:.2f}%')
        # Create new rows every 3 categories
        if (idx + 1) % 3 == 0 and (idx + 1) != len(categories):
            cols = st.columns(3)

    # Price trend visualization
    grouped_data['w/c'] = pd.to_datetime(grouped_data['w/c'])
    fig = px.line(grouped_data, x='w/c', y='prices_(€)', color='category',
                  title=f'Price Changes by Category - {supermarket}')
    fig.update_layout(
        xaxis_title='Week Commencing',
        yaxis_title='Average Prices by Category (€)',
        xaxis=dict(tickmode='auto', tickformat='%Y-%m-%d')
    )
    st.plotly_chart(fig)
    
    # Data section
    st.subheader('Data')
    with st.expander(label=f'Grouped Data for {supermarket}', expanded=False):
        st.dataframe(grouped_data)

def create_grouped_data(supermarket):
    """
    Create grouped data from MongoDB collection
    """
    # Query MongoDB for the selected supermarket
    query = {"supermarket": supermarket}
    projection = {"_id": 0, "category": 1, "prices_(€)": 1, "date": 1}
    data = pd.DataFrame(list(collection.find(query, projection)))

    if data.empty:
        return pd.DataFrame()

    # Convert and process dates
    data['date'] = pd.to_datetime(data['date'], format='%Y%m%d')
    data.set_index('date', inplace=True)

    # Group data by category and week
    grouped = data.groupby(['category', pd.Grouper(freq='7D')])['prices_(€)'].mean().reset_index()
    grouped['change_(%)'] = grouped.groupby('category')['prices_(€)'].pct_change() * 100
    grouped.rename(columns={'date': 'w/c'}, inplace=True)
    
    return grouped.fillna(0)

def create_price_metrics(supermarket):
    """
    Calculate price metrics from MongoDB data
    """
    grouped_data = create_grouped_data(supermarket)
    
    if grouped_data.empty:
        return ([], {}, {}, 0, 0, pd.DataFrame())

    categories = grouped_data['category'].unique()
    metrics = {
        'final_prices': {},
        'final_percentage_changes': {},
        'total_price_change': 0,
        'total_initial_price': 0
    }

    for category in categories:
        category_data = grouped_data[grouped_data['category'] == category]
        initial_price = category_data['prices_(€)'].iloc[0]
        final_price = category_data['prices_(€)'].iloc[-1]
        final_change = category_data['change_(%)'].iloc[-1]

        metrics['final_prices'][category] = final_price
        metrics['final_percentage_changes'][category] = final_change
        metrics['total_price_change'] += final_price - initial_price
        metrics['total_initial_price'] += initial_price

    total_price_change_percentage = (metrics['total_price_change'] / metrics['total_initial_price']) * 100 if metrics['total_initial_price'] else 0

    return (
        categories,
        metrics['final_prices'],
        metrics['final_percentage_changes'],
        metrics['total_price_change'],
        total_price_change_percentage,
        grouped_data
    )

if __name__ == "__main__":
    main() 