from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BeralandScraper:
    """Scraper for extracting projects and Twitter accounts from Beraland ecosystem."""
    
    def __init__(self, headless=True, wait_time=1.5, progress_callback=None, status_callback=None):
        """
        Initialize the BeralandScraper.
        
        Args:
            headless (bool): Whether to run browser in headless mode
            wait_time (float): Time to wait between actions in seconds
            progress_callback (callable): Function to call with progress updates (0-1)
            status_callback (callable): Function to call with status text updates
        """
        self.url = "https://app.beraland.xyz/dl/Ecosystem"
        self.headless = headless
        self.wait_time = wait_time
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.driver = None
    
    def _update_status(self, text):
        """Update status text via callback if available."""
        logger.info(text)
        if self.status_callback:
            self.status_callback(text)
    
    def _update_progress(self, progress):
        """Update progress via callback if available."""
        if self.progress_callback:
            self.progress_callback(progress)
    
    def _setup_driver(self):
        """Set up and return a configured WebDriver."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self._update_status("Setting up Chrome WebDriver...")
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            return driver
        except Exception as e:
            self._update_status(f"Error setting up Chrome WebDriver: {e}")
            raise
    
    def _extract_twitter_handle(self, url):
        """Extract Twitter handle from URL."""
        if not url or url == "N/A":
            return "N/A"
        
        # Try standard Twitter URL format
        match = re.search(r'twitter\.com/([^/\?]+)', url)
        if match:
            return "@" + match.group(1)
        
        # Try x.com (Twitter rebranding)
        match = re.search(r'x\.com/([^/\?]+)', url)
        if match:
            return "@" + match.group(1)
            
        return url
    
    def _find_project_cards(self):
        """Find all project cards on the page using multiple selectors."""
        selectors = [
            ".project-card", 
            "div[role='gridcell']", 
            ".card", 
            ".grid-item",
            "[class*='card']",
            "[class*='project']"
        ]
        
        for selector in selectors:
            try:
                cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if cards and len(cards) > 0:
                    self._update_status(f"Found {len(cards)} project cards using selector: {selector}")
                    return cards
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        # Take screenshot for debugging
        self._update_status("No project cards found with standard selectors. Taking a screenshot for debugging.")
        self.driver.save_screenshot("debug_screenshot.png")
        
        # Last resort: try to find any clickable elements
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div")
            potential_cards = [e for e in elements if e.is_displayed() and e.size['width'] > 100 and e.size['height'] > 100]
            if potential_cards:
                self._update_status(f"Found {len(potential_cards)} potential project cards as fallback")
                return potential_cards[:20]  # Limit to first 20 to be safe
        except:
            pass
            
        return []
    
    def _process_project_card(self, card, index, total):
        """Process a single project card and extract information."""
        project_data = {
            "Project Name": "Unknown",
            "Category": "N/A",
            "Twitter URL": "N/A",
            "Twitter Handle": "N/A"
        }
        
        try:
            # Try to get project name from the card
            try:
                project_name_elem = card.find_element(By.CSS_SELECTOR, "h3, h4, .project-title, .title, [class*='title']")
                project_name = project_name_elem.text
            except:
                # Fallback to splitting text content
                project_name = card.text.split('\n')[0] if card.text else f"Project {index+1}"
            
            project_data["Project Name"] = project_name
            self._update_status(f"Processing {project_name} ({index+1}/{total})...")
            
            # Click on the card to open details
            card.click()
            time.sleep(self.wait_time)
            
            # Wait for details modal to appear
            modal_appeared = False
            for selector in [".modal", ".project-details", ".dialog", "[role='dialog']"]:
                try:
                    WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    modal_appeared = True
                    break
                except:
                    continue
            
            if not modal_appeared:
                self._update_status(f"Warning: Modal may not have appeared for {project_name}")
            
            # Get project category
            category_selectors = [".category", ".tags", ".project-type", ".label", "[class*='category']", "[class*='tag']"]
            for selector in category_selectors:
                try:
                    category_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    category = category_element.text
                    if category:
                        project_data["Category"] = category
                        break
                except:
                    continue
            
            # Get Twitter link
            twitter_selectors = [
                "a[href*='twitter.com']", 
                "a[href*='x.com']",
                "a[aria-label*='Twitter']",
                "a[aria-label*='twitter']",
                ".twitter-button", 
                "button[data-social='twitter']",
                "[class*='twitter']"
            ]
            
            for selector in twitter_selectors:
                try:
                    twitter_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in twitter_elements:
                        href = elem.get_attribute("href")
                        if href and ("twitter.com" in href or "x.com" in href):
                            project_data["Twitter URL"] = href
                            project_data["Twitter Handle"] = self._extract_twitter_handle(href)
                            break
                    if project_data["Twitter URL"] != "N/A":
                        break
                except:
                    continue
            
            # Close the modal - try multiple methods
            self._close_modal(project_name)
            
        except Exception as e:
            self._update_status(f"Error processing card {index+1}: {e}")
        
        return project_data
    
    def _close_modal(self, project_name):
        """Attempt to close the modal using multiple methods."""
        modal_closed = False
        
        # Method 1: Click close button
        close_selectors = [
            ".close-button", 
            "button[aria-label='Close']", 
            ".modal-close", 
            "button.close",
            "[class*='close']",
            "button[class*='close']"
        ]
        
        for selector in close_selectors:
            if modal_closed:
                break
            try:
                close_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in close_buttons:
                    if button.is_displayed():
                        button.click()
                        time.sleep(0.5)
                        modal_closed = True
                        break
            except:
                continue
        
        # Method 2: Press Escape key
        if not modal_closed:
            try:
                from selenium.webdriver.common.keys import Keys
                webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(0.5)
                modal_closed = True
            except:
                pass
        
        # Method 3: Click outside the modal
        if not modal_closed:
            try:
                # Try to find the modal overlay/backdrop
                backdrops = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".modal-backdrop, .overlay, .backdrop, [class*='overlay'], [class*='backdrop']")
                
                if backdrops:
                    for backdrop in backdrops:
                        if backdrop.is_displayed():
                            backdrop.click()
                            modal_closed = True
                            break
                
                if not modal_closed:
                    # Click at position 0,0 (usually outside any modal)
                    webdriver.ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            except:
                self._update_status(f"Warning: Could not close modal for {project_name}")
        
        return modal_closed
    
    def scrape_projects(self):
        """
        Main method to scrape Beraland ecosystem projects.
        
        Returns:
            pd.DataFrame: DataFrame containing project data
        """
        try:
            # Initialize WebDriver
            self.driver = self._setup_driver()
            
            # Open the webpage
            self._update_status("Opening Beraland Ecosystem page...")
            self.driver.get(self.url)
            
            # Wait for the page to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                )
                time.sleep(2)  # Additional wait to ensure JS loads
                self._update_status("Page loaded successfully")
            except TimeoutException:
                self._update_status("Warning: Page load timed out, but continuing anyway")
            
            # Find all project cards
            project_cards = self._find_project_cards()
            
            if not project_cards:
                self._update_status("No project cards found")
                return pd.DataFrame()
            
            # Prepare results list
            projects_data = []
            
            # Process each card
            for i, card in enumerate(project_cards):
                # Update progress
                self._update_progress((i + 1) / len(project_cards))
                
                # Process the card
                project_data = self._process_project_card(card, i, len(project_cards))
                projects_data.append(project_data)
                
                # Short pause between projects
                time.sleep(0.5)
            
            # Create DataFrame
            df = pd.DataFrame(projects_data)
            
            # Add timestamp
            df["Extracted At"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self._update_status(f"Scraping completed! Found {len(projects_data)} projects.")
            return df
            
        except Exception as e:
            self._update_status(f"An error occurred during scraping: {e}")
            raise
            
        finally:
            # Clean up
            if self.driver:
                self.driver.quit()
