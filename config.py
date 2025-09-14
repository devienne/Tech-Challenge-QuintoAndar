"""
Configuration settings for QuintoAndar scraper
"""

# Scraping configuration
BAIRRO = "tatuape"
BASE_URL = "https://www.quintoandar.com.br"
LISTING_URL = f"{BASE_URL}/alugar/imovel/{BAIRRO}-sao-paulo-sp-brasil"

# Browser configuration
WAIT_TIME = 12
HEADLESS = True
PAGE_LOAD_TIMEOUT = 30

# HTTP client configuration
CONCURRENCY = 8  # Reduced from 12 for better stability
TIMEOUT = 20.0
RETRIES = 3
RATE_LIMIT_DELAY = 0.5

# Headers to mimic real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.7,en;q=0.6",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# CSS selectors for data extraction
SELECTORS = {
    "listing_cards": "div[data-testid='house-card-container-rent'] a",
    "load_more_btn": "button#see-more, button[data-testid='load-more-button']",
    "title": "h1[data-testid='listing-title'], h1, h2",
    "address_container": "div[data-testid='address-container']",
    "address_paragraphs": "div[data-testid='address-container'] p",
    "main_info": "div[data-testid='house-main-info'] .MainInfo_iconDescriptionWrapper__St8RA",
    "price_table": "ul[data-testid='listing-price-table'] li",
    "price_labels": "span, h4",
    "price_values": "div > p, div > h4",
}

# Output configuration
OUTPUT_FILE = f"quintoandar_{BAIRRO}.csv"
LOG_LEVEL = "INFO"