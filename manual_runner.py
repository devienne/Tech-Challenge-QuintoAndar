"""
Manual runner for step-by-step control of the scraping process
"""

import asyncio
import pandas as pd
from datetime import datetime
import nest_asyncio

# Enable nested event loops for Jupyter compatibility
nest_asyncio.apply()

from config import BAIRRO
from url_collector import collect_urls
from http_client import fetch_properties
from models import PropertyInfo


async def run_scraper_manual():
    """Run scraper with manual control and return DataFrame"""
    
    print(f"=== Manual QuintoAndar Scraper for {BAIRRO} ===")
    
    # Step 1: Collect URLs
    print(f"\n1. Collecting URLs (limit: {MAX_URLS})...")
    urls = collect_urls(MAX_URLS)
    print(f"Collected {len(urls)} URLs")
    
    if not urls:
        print("No URLs found. Exiting.")
        return None
    
    # Optional: Limit to first N URLs for testing
    # urls = urls[:10]  # Uncomment to test with only 10 URLs
    
    # Step 2: Fetch property data
    print(f"\n2. Fetching data for {len(urls)} properties...")
    properties = await fetch_properties(urls)
    print(f"Fetched {len(properties)} properties")
    
    # Step 3: Convert to DataFrame
    print("\n3. Converting to DataFrame...")
    data = [prop.to_dict() for prop in properties]
    df = pd.DataFrame(data)
    
    # Reorder columns for better readability
    if not df.empty:
        first_cols = [
            "url", "status", "title", "address_street", "area", "quartos", 
            "suite", "banheiros", "vagas", "andar", "pet", "mobiliado", "metro_proximo"
        ]
        price_cols = [col for col in df.columns if col not in first_cols]
        ordered_cols = [col for col in first_cols if col in df.columns] + price_cols
        df = df[ordered_cols]
    
    # Step 4: Display statistics
    print("\n4. Results Summary:")
    print(f"Total properties: {len(df)}")
    print(f"Successfully parsed: {len(df[df['status'] == 'success'])}")
    print(f"With addresses: {len(df[df['address_street'].notna()])}")
    print(f"Average area: {df['area'].str.extract('(\d+)').astype(float).mean():.1f} m²")
    print(f"Room distribution:")
    print(df['quartos'].value_counts().head())
    
    # Step 5: Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quintoandar_{BAIRRO}_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n5. Saved to: {filename}")
    
    return df


def load_existing_data(filename: str = None):
    """Load existing scraped data"""
    if filename is None:
        # Find the most recent file
        import glob
        files = glob.glob(f"quintoandar_{BAIRRO}_*.csv")
        if not files:
            print("No existing data files found")
            return None
        filename = max(files)  # Most recent by name
    
    try:
        df = pd.read_csv(filename, encoding='utf-8-sig')
        print(f"Loaded {len(df)} records from {filename}")
        return df
    except FileNotFoundError:
        print(f"File {filename} not found")
        return None


def analyze_data(df):
    """Analyze the scraped data"""
    if df is None or df.empty:
        print("No data to analyze")
        return
    
    print("=== DATA ANALYSIS ===")
    print(f"\nDataset shape: {df.shape}")
    print(f"Successful extractions: {len(df[df['status'] == 'success'])}")
    
    # Address extraction success
    with_address = df['address_street'].notna().sum()
    print(f"Properties with addresses: {with_address} ({with_address/len(df)*100:.1f}%)")
    
    # Property types (inferred from title)
    if 'title' in df.columns:
        apt_count = df['title'].str.contains('Apartamento', na=False).sum()
        house_count = df['title'].str.contains('Casa', na=False).sum()
        studio_count = df['title'].str.contains('Studio', na=False).sum()
        print(f"\nProperty types:")
        print(f"  Apartments: {apt_count}")
        print(f"  Houses: {house_count}")
        print(f"  Studios: {studio_count}")
    
    # Room distribution
    if 'quartos' in df.columns:
        print(f"\nRoom distribution:")
        room_dist = df['quartos'].value_counts().sort_index()
        for rooms, count in room_dist.items():
            print(f"  {rooms} quartos: {count} properties")
    
    # Area statistics
    if 'area' in df.columns:
        area_nums = df['area'].str.extract('(\d+)').astype(float)
        area_nums = area_nums.dropna()
        if not area_nums.empty:
            print(f"\nArea statistics:")
            print(f"  Mean: {area_nums.mean():.1f} m²")
            print(f"  Median: {area_nums.median():.1f} m²")
            print(f"  Range: {area_nums.min():.0f} - {area_nums.max():.0f} m²")
    
    # Price analysis (if available)
    price_cols = [col for col in df.columns if 'R$' in str(df[col].iloc[0] if len(df) > 0 else '')]
    if price_cols:
        print(f"\nPrice columns available: {len(price_cols)}")
        for col in price_cols[:3]:  # Show first 3 price columns
            print(f"  {col}: {df[col].notna().sum()} properties")


# Main functions for different use cases
async def quick_test_run(limit=10):
    """Quick test with limited URLs"""
    print(f"=== Quick Test Run (limit: {limit}) ===")
    
    # Just test the fetching part with a few URLs
    from url_collector import URLCollector
    collector = URLCollector()
    # You can manually provide a few URLs here for testing
    test_urls = [
        "https://www.quintoandar.com.br/imovel/89306607812345123456789",  # Replace with real URLs
    ]
    
    if test_urls:
        properties = await fetch_properties(test_urls[:limit])
        data = [prop.to_dict() for prop in properties]
        df = pd.DataFrame(data)
        return df
    else:
        print("No test URLs provided")
        return None


if __name__ == "__main__":
    # Choose what you want to do:
    
    # Option 1: Run complete scraper
    df = asyncio.run(run_scraper_manual())
    
    # Option 2: Load existing data
    # df = load_existing_data()
    
    # Option 3: Quick test
    # df = asyncio.run(quick_test_run(limit=5))
    
    # Analyze the results
    if df is not None:
        analyze_data(df)
        print(f"\nDataFrame is ready! Shape: {df.shape}")
        print("You can now work with the 'df' variable")