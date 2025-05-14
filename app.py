from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import re

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Setup WebDriver
# Note: You need to download chromedriver and specify its path here
webdriver_service = Service('path/to/chromedriver')  # Update this path
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Function to extract Twitter handle from a Twitter URL
def extract_twitter_handle(url):
    if not url:
        return "N/A"
    match = re.search(r'twitter\.com/([^/\?]+)', url)
    if match:
        return "@" + match.group(1)
    return url

# Main scraping function
def scrape_beraland_ecosystem():
    # Open the webpage
    print("Opening Beraland Ecosystem page...")
    driver.get("https://app.beraland.xyz/dl/Ecosystem")
    
    # Wait for the page to load (adjust timeout as needed)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".ecosystem-grid, .project-card, div[role='grid']"))
    )
    print("Page loaded successfully")
    
    # Find all project cards
    # Note: The actual selector may differ based on the website's HTML structure
    try:
        project_cards = driver.find_elements(By.CSS_SELECTOR, ".project-card, .card, div[role='gridcell']")
        print(f"Found {len(project_cards)} project cards")
    except Exception as e:
        print(f"Error finding project cards: {e}")
        project_cards = []
    
    # Prepare results list
    projects_data = []
    
    # Loop through each project card
    for i, card in enumerate(project_cards):
        try:
            # Extract project name from the card
            project_name = card.text.split('\n')[0] if card.text else f"Project {i+1}"
            print(f"Processing {project_name}...")
            
            # Click on the card to open details
            card.click()
            
            # Wait for details modal to appear
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".modal, .project-details, .dialog"))
            )
            
            # Extract details
            time.sleep(1)  # Short pause to ensure content is loaded
            
            # Get project category
            try:
                category_element = driver.find_element(By.CSS_SELECTOR, ".category, .tags, .project-type")
                category = category_element.text
            except:
                category = "N/A"
            
            # Get Twitter link
            twitter_url = ""
            try:
                # Look for Twitter button/link
                twitter_element = driver.find_element(
                    By.CSS_SELECTOR, 
                    "a[href*='twitter'], button[data-social='twitter'], .twitter-link"
                )
                twitter_url = twitter_element.get_attribute("href")
            except:
                twitter_url = "N/A"
            
            # Extract Twitter handle from URL
            twitter_handle = extract_twitter_handle(twitter_url)
            
            # Add to results
            projects_data.append({
                "Project Name": project_name,
                "Category": category,
                "Twitter URL": twitter_url,
                "Twitter Handle": twitter_handle
            })
            
            # Close the modal
            try:
                close_button = driver.find_element(By.CSS_SELECTOR, ".close-button, button[aria-label='Close']")
                close_button.click()
                time.sleep(0.5)  # Wait for modal to close
            except:
                # Try pressing ESC key if button not found
                from selenium.webdriver.common.keys import Keys
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Error processing card {i+1}: {e}")
            continue
    
    return projects_data

# Run the scraper
try:
    print("Starting the scraper...")
    projects_list = scrape_beraland_ecosystem()
    
    # Save to CSV
    with open('beraland_projects.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Project Name', 'Category', 'Twitter URL', 'Twitter Handle']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for project in projects_list:
            writer.writerow(project)
    
    print(f"Scraping completed. Found {len(projects_list)} projects. Data saved to beraland_projects.csv")
    
    # Display results
    print("\nResults:")
    for project in projects_list:
        print(f"{project['Project Name']} ({project['Category']}) - {project['Twitter Handle']}")
    
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Clean up
    driver.quit()
    print("Browser closed")
