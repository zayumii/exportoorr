from setuptools import setup, find_packages

setup(
    name="exportoorr",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.32.0",
        "selenium>=4.18.1",
        "webdriver-manager>=4.0.1",
        "pandas>=2.1.4",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
    ],
)
