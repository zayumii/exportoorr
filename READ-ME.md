# Beraland Ecosystem Exporter

A Streamlit app that exports projects and their Twitter accounts from the Beraland ecosystem.

![App Screenshot](docs/images/app_screenshot.png)

## Features

- 🔍 Automatically scrapes the Beraland Ecosystem page
- 📊 Extracts project names, categories, and Twitter accounts
- 📥 Exports data in CSV and Excel formats
- 🚀 Easy to use with a simple interface
- 🛠️ No technical skills required to run

## Live Demo

[Access the live demo here](#) (Coming soon)

## Quick Start

### Option 1: Run locally

1. Clone this repository:
```bash
git clone https://github.com/yourusername/beraland-ecosystem-exporter.git
cd beraland-ecosystem-exporter
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run app.py
```

### Option 2: Run with Docker

```bash
docker pull yourusername/beraland-exporter
docker run -p 8501:8501 yourusername/beraland-exporter
```

Then open your browser and go to http://localhost:8501

## How It Works

This app uses Selenium WebDriver to:
1. Navigate to the Beraland ecosystem page
2. Find all project cards
3. Click each card to view details
4. Extract information including Twitter accounts
5. Compile the data into a downloadable format

## Repository Structure

```
beraland-ecosystem-exporter/
├── app.py                  # Main Streamlit application
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── scraper.py          # Web scraping functionality
│   └── data_helpers.py     # Data processing helpers
├── docs/                   # Documentation
│   └── images/             # Screenshots and images
├── tests/                  # Tests
│   ├── __init__.py
│   └── test_scraper.py     # Test cases for scraper
├── .gitignore
├── requirements.txt
├── Dockerfile
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Always ensure you're following websites' terms of service when scraping data.
