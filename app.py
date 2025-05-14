import streamlit as st
from utils.scraper import BeralandScraper
from utils.data_helpers import get_csv_download_link, get_excel_download_link
import time
import os

# Set page config
st.set_page_config(
    page_title="Beraland Ecosystem Exporter",
    page_icon="🐻",
    layout="wide"
)

# App title and branding
def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🐻 Beraland Ecosystem Exporter")
        st.markdown("""
        Export projects and their Twitter accounts from the Beraland ecosystem with one click.
        """)
    with col2:
        # GitHub link
        st.markdown("""
        <div style="text-align: right; margin-top: 20px;">
            <a href="https://github.com/yourusername/beraland-ecosystem-exporter" target="_blank">
                <img src="https://img.shields.io/github/stars/yourusername/beraland-ecosystem-exporter?style=social" alt="GitHub Repo">
            </a>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Render the header
    render_header()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Exporter", "Results", "Help"])
    
    with tab1:
        st.subheader("Export Projects")
        
        # Options
        col1, col2 = st.columns(2)
        with col1:
            headless = st.checkbox("Run in headless mode", value=True, 
                                  help="Run browser without UI (faster but you won't see the process)")
        with col2:
            wait_time = st.slider("Wait time between actions (seconds)", 0.5, 3.0, 1.5,
                                 help="Increase this if the scraper is missing information")
        
        # Start button
        start_col, _ = st.columns([1, 2])
        with start_col:
            start_button = st.button("🚀 Start Scraping", type="primary", use_container_width=True)
        
        # Progress indicators
        progress_bar = st.progress(0)
        status_container = st.container()
        status_text = status_container.empty()
        
        # Results placeholder
        if "projects_df" not in st.session_state:
            st.session_state.projects_df = None
    
    with tab2:
        st.subheader("Extracted Data")
        
        # Show results if available
        if st.session_state.get("projects_df") is not None and not st.session_state.projects_df.empty:
            st.dataframe(st.session_state.projects_df, use_container_width=True)
            
            # Download options
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(get_csv_download_link(st.session_state.projects_df), unsafe_allow_html=True)
            with col2:
                st.markdown(get_excel_download_link(st.session_state.projects_df), unsafe_allow_html=True)
            
            # Stats
            st.metric("Total Projects", len(st.session_state.projects_df))
        else:
            st.info("No data available yet. Run the scraper in the Exporter tab to see results here.")
    
    with tab3:
        st.subheader("Help & Information")
        
        st.markdown("""
        ### How to use this app
        
        1. Go to the **Exporter** tab
        2. Click the **Start Scraping** button
        3. Wait for the scraping process to complete
        4. View and download results in the **Results** tab
        
        ### What this app does
        
        This app automatically visits the [Beraland Ecosystem page](https://app.beraland.xyz/dl/Ecosystem) and extracts information about all projects, including:
        
        - Project names
        - Categories/tags
        - Twitter accounts
        
        ### Troubleshooting
        
        If the app isn't working correctly:
        
        - Increase the **Wait time** slider to give the page more time to load
        - Uncheck **Run in headless mode** to see what's happening
        - Make sure you have a stable internet connection
        - Try running the app again if it fails
        
        ### About
        
        This app was created as an open-source tool to help track and analyze the Berachain ecosystem.
        
        [View source code on GitHub](https://github.com/yourusername/beraland-ecosystem-exporter)
        """)
    
    # Run the scraper when button is clicked
    if start_button:
        status_text.text("Setting up web driver...")
        
        # Initialize the scraper
        scraper = BeralandScraper(
            headless=headless,
            wait_time=wait_time,
            progress_callback=lambda progress: progress_bar.progress(progress),
            status_callback=lambda text: status_text.text(text)
        )
        
        try:
            # Run the scraper
            df = scraper.scrape_projects()
            
            # Store results in session state
            st.session_state.projects_df = df
            
            # Show success and switch to Results tab
            if df is not None and not df.empty:
                status_text.success(f"✅ Successfully extracted {len(df)} projects!")
                time.sleep(1)
                st.experimental_rerun()  # Switch to Results tab
            else:
                status_text.error("No data was found. Please try again or adjust settings.")
        
        except Exception as e:
            status_text.error(f"An error occurred: {str(e)}")
            
            # Debug info
            with st.expander("Error details"):
                st.code(str(e))
                
                # Show screenshot if available
                debug_screenshot = "debug_screenshot.png"
                if os.path.exists(debug_screenshot):
                    st.image(debug_screenshot, caption="Debug screenshot")

if __name__ == "__main__":
    main()
