import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Beraland Data Exporter",
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("Beraland Data Exporter")
st.markdown("Export data from Beraland easily")

# Create sidebar for inputs
with st.sidebar:
    st.header("Settings")
    url = st.text_input("Enter Beraland URL", "https://example.com/beraland")
    
    if st.button("Scrape Data"):
        with st.spinner("Scraping data..."):
            try:
                # Use requests and BeautifulSoup instead of Selenium
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                st.success("Data scraped successfully!")
                
                # Store the data in session state
                st.session_state.soup = soup
                st.session_state.scraped = True
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Main content area
st.header("Extracted Data")
st.info("Click 'Scrape Data' in the sidebar to start extraction")

# Create tabs for different views
tab1, tab2 = st.tabs(["Data Table", "Analysis"])

with tab1:
    st.subheader("Data Table")
    if 'scraped' in st.session_state and st.session_state.scraped:
        soup = st.session_state.soup
        # Example: Extract table data (replace with your actual extraction logic)
        tables = soup.find_all('table')
        if tables:
            for i, table in enumerate(tables):
                st.write(f"Table {i+1}")
                # Convert HTML table to pandas DataFrame
                df_list = pd.read_html(str(table))
                if df_list:
                    st.dataframe(df_list[0])
        else:
            st.write("No tables found on the page")
    
with tab2:
    st.subheader("Data Analysis")
    if 'scraped' in st.session_state and st.session_state.scraped:
        soup = st.session_state.soup
        # Example: Simple analysis (replace with your actual analysis)
        st.write("Page Title:", soup.title.string if soup.title else "No title found")
        st.write("Number of links:", len(soup.find_all('a')))
        st.write("Number of images:", len(soup.find_all('img')))

# Footer
st.markdown("---")
st.markdown("Created with ❤️ by [zayumii](https://github.com/zayumii/exportoorr)")
