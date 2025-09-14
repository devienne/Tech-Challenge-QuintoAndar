"""
URL collector using Selenium for dynamic content loading
"""

import time
import logging
from typing import List, Set
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, 
    StaleElementReferenceException, 
    ElementClickInterceptedException,
    WebDriverException
)

from config import LISTING_URL, WAIT_TIME, HEADLESS, PAGE_LOAD_TIMEOUT, SELECTORS


class URLCollector:
    """Collects property URLs using Selenium"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger(__name__)
        
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with optimal settings"""
        options = Options()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--incognito")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if HEADLESS:
            options.add_argument("--headless=new")
        
        # Performance optimizations
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")  # We don't need JS for this
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        
        # Remove automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _wait_for_initial_load(self) -> bool:
        """Wait for initial page load and first cards"""
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["listing_cards"]))
            )
            time.sleep(2)  # Buffer for lazy loading
            return True
        except TimeoutException:
            self.logger.error("Initial page load failed - no listing cards found")
            return False
    
    def _collect_current_urls(self) -> Set[str]:
        """Collect all URLs currently visible on page"""
        urls = set()
        try:
            cards = self.driver.find_elements(By.CSS_SELECTOR, SELECTORS["listing_cards"])
            for card in cards:
                try:
                    href = card.get_attribute("href")
                    if href and href.startswith("https"):
                        urls.add(href)
                except StaleElementReferenceException:
                    continue  # Element changed, skip it
        except Exception as e:
            self.logger.warning(f"Error collecting URLs: {e}")
        
        return urls
    
    def _find_load_more_button(self):
        """Find the load more button"""
        try:
            return self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["load_more_btn"]))
            )
        except TimeoutException:
            return None
    
    def _click_load_more(self, button) -> bool:
        """Attempt to click the load more button"""
        try:
            # Check if button is disabled
            if (button.get_attribute("disabled") or 
                button.get_attribute("aria-disabled") == "true"):
                return False
            
            # Scroll to button
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", button
            )
            time.sleep(1)
            
            # Try regular click first
            try:
                button.click()
            except (ElementClickInterceptedException, StaleElementReferenceException):
                # Fallback to JavaScript click
                self.driver.execute_script("arguments[0].click();", button)
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Failed to click load more button: {e}")
            return False
    
    def _wait_for_new_content(self, previous_count: int) -> bool:
        """Wait for new content to load after clicking load more"""
        try:
            self.wait.until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, SELECTORS["listing_cards"])) > previous_count
            )
            time.sleep(1)  # Small buffer for complete loading
            return True
        except TimeoutException:
            return False
    
    def collect_all_urls(self) -> List[str]:
        """Main method to collect all property URLs"""
        self.logger.info(f"Starting URL collection from: {LISTING_URL}")
        
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, WAIT_TIME)
        
        try:
            # Load initial page
            self.driver.get(LISTING_URL)
            
            if not self._wait_for_initial_load():
                return []
            
            all_urls = set()
            no_progress_count = 0
            max_no_progress = 3
            
            while len(all_urls)<=100:
                # Collect current URLs
                current_urls = self._collect_current_urls()
                new_urls = current_urls - all_urls
                
                if new_urls:
                    all_urls.update(new_urls)
                    self.logger.info(f"Found {len(new_urls)} new URLs. Total: {len(all_urls)}")
                    no_progress_count = 0
                else:
                    no_progress_count += 1
                    self.logger.info(f"No new URLs found. No progress count: {no_progress_count}")
                
                # Check for load more button
                button = self._find_load_more_button()
                if not button:
                    self.logger.info("No load more button found - reached end")
                    break
                
                # Try to click load more
                previous_count = len(self.driver.find_elements(By.CSS_SELECTOR, SELECTORS["listing_cards"]))
                
                if not self._click_load_more(button):
                    self.logger.info("Load more button is disabled - reached end")
                    break
                
                # Wait for new content
                if not self._wait_for_new_content(previous_count):
                    no_progress_count += 1
                    self.logger.warning(f"No new content loaded after click. Attempt {no_progress_count}")
                    
                    if no_progress_count >= max_no_progress:
                        self.logger.info("Multiple failed attempts - assuming we've reached the end")
                        break
            
            final_urls = list(all_urls)
            self.logger.info(f"Collection complete. Total URLs collected: {len(final_urls)}")
            return final_urls
            
        except WebDriverException as e:
            self.logger.error(f"WebDriver error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error during URL collection: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()


def collect_urls() -> List[str]:
    """Convenience function to collect URLs"""
    collector = URLCollector()
    return collector.collect_all_urls()