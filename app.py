import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# Set page config
st.set_page_config(
    page_title="Beraland Data Exporter",
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("Beraland Data Exporter")
st.markdown("Export data from Beraland easily")

# Sidebar for input
with st.sidebar:
    st.header("Settings")
    url = st.text_input("Enter Beraland URL", "https://app.beraland.xyz/dl/Ecosystem")

    if st.button("Scrape Data"):
        with st.spinner("Scraping data..."):
            try:
                def scrape_beraland_handles(scrape_url):
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }
                    response = requests.get(scrape_url, headers=headers)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, "html.parser")

                    # Grab all hrefs and filter twitter handles manually
                    handles = []
                    links = soup.find_all("a", href=True)
                    for link in links:
                        href = link.get("href")
                        if href and "twitter.com" in href:
                            match = re.search(r"twitter\.com/([^/?]+)", href)
                            if match:
                                handle = match.group(1)
                                if handle.lower() != "share":
                                    handles.append(handle)

                    return sorted(set(handles))

                handles = scrape_beraland_handles(url)
                df = pd.DataFrame(handles, columns=["Twitter Handle"])
                st.session_state.df = df
                st.session_state.scraped = True
                st.success("Data scraped successfully!")

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
        df = st.session_state.df
        st.dataframe(df)

with tab2:
    st.subheader("Data Analysis")
    if 'scraped' in st.session_state and st.session_state.scraped:
        df = st.session_state.df
        st.write(f"Total Twitter handles found: {len(df)}")
        st.write("Example Handles:", df.head())

# Footer
st.markdown("---")
st.markdown("Created with ❤️ by [zayumii](https://github.com/zayumii/exportoorr)")
