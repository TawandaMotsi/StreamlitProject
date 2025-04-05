import streamlit as st

def main():
    st.title("The Process")
    st.write("This page will explain, in detail, the end to end process for the webscraping, data processing and data analysis of the supermarket data.")

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

    # Create a dropdown (selectbox)


    st.title("🧠 Web Scraping Dashboard")

    with st.expander("Code: Web Scraping Functions"):
        st.markdown("""
        This section contains the core scraping logic:

        1. **Get HTML content** from the product page  
        2. **Extract product name**, price, and price per unit  
        3. **Handle errors** and missing data  
        4. **Return structured results** for display and storage
        """)

            
if __name__ == "__main__":
    main()
