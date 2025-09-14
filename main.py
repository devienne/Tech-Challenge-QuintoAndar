"""
Main application for QuintoAndar property scraper
"""
import os
import asyncio
import logging
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
from typing import List

# Try to enable nested event loops for Jupyter compatibility
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

from config import OUTPUT_FILE, LOG_LEVEL, BAIRRO
from url_collector import collect_urls
from http_client import fetch_properties
from models import PropertyInfo


def setup_logging() -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

@staticmethod
def create_data_directories():
    data = "database/data"
    urls = "database/urls"
    os.makedirs(data, exist_ok=True)
    os.makedirs(urls, exist_ok=True)
    return data, urls

def save_results(properties: List[PropertyInfo], filename: str = None) -> None:
    """Save results to CSV file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quintoandar_{BAIRRO}_{timestamp}.csv"
    
    # Convert PropertyInfo objects to dictionaries
    data = [prop.to_dict() for prop in properties]
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Reorder columns for better readability
    if not df.empty:
        first_cols = [
            "url", "status", "title", "address_street", "area", "quartos", 
            "suite", "banheiros", "vagas", "andar", "pet", "mobiliado", "metro_proximo"
        ]
        
        # Add price columns that exist in the data
        price_cols = [col for col in df.columns if col not in first_cols]
        ordered_cols = [col for col in first_cols if col in df.columns] + price_cols
        df = df[ordered_cols]
    
    # create datavbase/data folder if not yet existent
    data_folder, _ = create_data_directories()
    # Save to CSV
    filepath = os.path.join(data_folder, filename)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    # Print statistics
    total = len(df)
    successful = len(df[df['status'] == 'success'])
    with_address = len(df[df['address_street'].notna()])
    
    print(f"\nResults saved to: {filename}")
    print(f"Total properties: {total}")
    print(f"Successfully parsed: {successful}")
    print(f"With addresses: {with_address}")
    print(f"Success rate: {successful/total*100:.1f}%")
    print(f"Address extraction rate: {with_address/total*100:.1f}%")


def load_urls_from_file(filename: str) -> List[str]:
    """Load URLs from a text file (one URL per line)"""
    try:
        # create datavbase/data folder if not yet existent
        _, urls_folder = create_data_directories()
        # Save to CSV
        filepath = os.path.join(urls_folder, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(urls)} URLs from {filename}")
        return urls
    except FileNotFoundError:
        print(f"File {filepath} not found")
        return []


def save_urls_to_file(urls: List[str], filename: str = None) -> None:
    """Save URLs to a text file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"urls_{BAIRRO}_{timestamp}.txt"

    # create datavbase/data folder if not yet existent
    _, urls_folder = create_data_directories()
    # Save to CSV
    filepath = os.path.join(urls_folder, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(f"{url}\n")
    
    print(f"Saved {len(urls)} URLs to {filename}")


async def main():
    """Main application entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("=== QuintoAndar Property Scraper ===")
    print(f"Target neighborhood: {BAIRRO}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Collect URLs
        print("\n1. Collecting property URLs...")
        
        # Check if we should load URLs from file
        urls_file = f"urls_{BAIRRO}.txt"
        if Path(urls_file).exists():
            response = input(f"Found existing URLs file: {urls_file}. Use it? (y/n): ").strip().lower()
            if response == 'y':
                urls = load_urls_from_file(urls_file)
            else:
                urls = collect_urls()
                if urls:
                    save_urls_to_file(urls)
        else:
            urls = collect_urls()
            if urls:
                save_urls_to_file(urls)
        
        if not urls:
            print("No URLs collected. Exiting.")
            return
        
        print(f"Collected {len(urls)} property URLs")
        
        # Step 2: Fetch property data
        print(f"\n2. Fetching property data...")
        properties = await fetch_properties(urls)
        
        if not properties:
            print("No property data fetched. Exiting.")
            return
        
        # Step 3: Save results
        print(f"\n3. Saving results...")
        save_results(properties)
        
        print(f"\nScraping completed successfully!")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        logger.info("Scraping interrupted by user")
    except Exception as e:
        print(f"\nError during scraping: {e}")
        logger.error(f"Error during scraping: {e}", exc_info=True)


def run_scraper():
    """Entry point that handles both regular Python and Jupyter environments"""
    try:
        # Try to run in the current event loop (Jupyter)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in Jupyter, create a task
            task = asyncio.create_task(main())
            return task
        else:
            # Regular Python environment
            return asyncio.run(main())
    except RuntimeError:
        # No event loop, regular Python environment
        return asyncio.run(main())


if __name__ == "__main__":
    run_scraper()