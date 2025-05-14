import streamlit as st
import pandas as pd
from playwright.sync_api import sync_playwright
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
                    handles = []
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=True)
                        page = browser.new_page()
                        page.goto(scrape_url, timeout=60000)
                        page.wait_for_selector("a[href^='https://twitter.com/']")

                        links = page.query_selector_all("a[href^='https://twitter.com/']")
                        for link in links:
                            href = link.get_attribute("href")
                            match = re.search(r"twitter\\.com/([^/?]+)", href)
                            if match:
                                handle = match.group(1)
                                if handle.lower() != "share":
                                    handles.append(handle)

                        browser.close()
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
