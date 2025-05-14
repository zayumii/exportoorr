import streamlit as st
from utils.scraper import BeralandScraper
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

# Initialize session state
if 'scraper' not in st.session_state:
    st.session_state.scraper = None

# Function to initialize or get scraper
def get_scraper():
    if st.session_state.scraper is None:
        with st.spinner("Initializing scraper..."):
            try:
                st.session_state.scraper = BeralandScraper()
                st.success("Scraper initialized successfully!")
            except Exception as e:
                st.error(f"Failed to initialize scraper: {str(e)}")
                st.info("This app requires Chrome browser to be installed on the server. If you're running on Streamlit Cloud, please check the logs.")
    return st.session_state.scraper

# Create sidebar for inputs
with st.sidebar:
    st.header("Settings")
    url = st.text_input("Enter Beraland URL", "https://example.com/beraland")
    
    if st.button("Scrape Data"):
        scraper = get_scraper()
        if scraper:
            with st.spinner("Scraping data..."):
                result = scraper.scrape_data(url)
                if result["status"] == "success":
                    st.success("Data scraped successfully!")
                    # Process and display data here
                else:
                    st.error(f"Error: {result['message']}")

# Main content area
st.header("Extracted Data")
st.info("Click 'Scrape Data' in the sidebar to start extraction")

# Create tabs for different views
tab1, tab2 = st.tabs(["Data Table", "Analysis"])

with tab1:
    st.subheader("Data Table")
    # Display data table here when available
    
with tab2:
    st.subheader("Data Analysis")
    # Display analysis here when available

# Footer
st.markdown("---")
st.markdown("Created with ❤️ by [zayumii](https://github.com/zayumii/exportoorr)")

# Clean up when the app is done
def cleanup():
    if st.session_state.scraper:
        st.session_state.scraper.close()

# Register the cleanup function
import atexit
atexit.register(cleanup)
