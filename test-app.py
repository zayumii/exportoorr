import streamlit as st

st.title("Selenium Test App")

# Test if selenium can be imported
try:
    import selenium
    st.success(f"Selenium import successful! Version: {selenium.__version__}")
except ImportError as e:
    st.error(f"Failed to import selenium: {str(e)}")
    
# Test if webdriver can be imported
try:
    from selenium import webdriver
    st.success("Webdriver import successful!")
except ImportError as e:
    st.error(f"Failed to import webdriver: {str(e)}")

# Display Python environment info
import sys
st.subheader("Python Environment Info")
st.write(f"Python version: {sys.version}")

# Display installed packages
st.subheader("Installed Packages")
import pkg_resources
installed_packages = sorted([f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set])
st.code("\n".join(installed_packages))
