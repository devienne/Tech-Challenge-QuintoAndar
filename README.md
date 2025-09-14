# QuintoAndar Property Scraper

## Features

- **Improved Address Extraction**: Multiple fallback strategies to capture property addresses
- **Modular Architecture**: Clean separation of concerns with dedicated classes
- **Async HTTP Requests**: Fast, concurrent data fetching with proper rate limiting
- **Comprehensive Error Handling**: Robust error recovery and logging
- **Progress Tracking**: Real-time progress updates during scraping
- **Data Persistence**: Automatic saving of URLs and results with timestamps
- **Jupyter Compatibility**: Works in both regular Python and Jupyter environments

## Installation

1. Clone or download the scraper files
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure you have Chrome browser installed (required for Selenium)

## Project Structure

```
├── database           # data base where scrapped data and urls are saved
    ├── data           # scrapped ata folder
    ├── urls           # urls folder
├── config.py          # Configuration settings
├── models.py          # Data models and property information structure
├── url_collector.py   # Selenium-based URL collection
├── data_parser.py     # HTML parsing and data extraction
├── http_client.py     # Async HTTP client for fetching pages
├── main.py            # Main application entry point
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Usage

### Basic Usage

Run the scraper for the default neighborhood (Jaçanã):

```bash
python main.py
```

### Configuration Options

Key settings in `config.py`:

- `BAIRRO`: Target neighborhood slug
- `CONCURRENCY`: Number of concurrent HTTP requests (default: 8)
- `HEADLESS`: Run browser in headless mode (default: True)
- `TIMEOUT`: HTTP request timeout in seconds
- `RETRIES`: Number of retry attempts for failed requests

## How It Works

1. **URL Collection** (`url_collector.py`):
   - Uses Selenium to navigate the listing page
   - Automatically clicks "Load More" buttons until all listings are found
   - Handles dynamic content loading and rate limiting
   - Saves collected URLs to a text file for reuse

2. **Data Extraction** (`data_parser.py`):
   - Multiple address extraction strategies:
     - JSON-LD structured data (most reliable)
     - DOM element parsing with various selectors
     - Breadcrumb and navigation analysis
     - Pattern matching for common address formats
   - Extracts property details (rooms, area, amenities)
   - Parses price information from tables

3. **HTTP Fetching** (`http_client.py`):
   - Async HTTP/2 requests for fast data retrieval
   - Automatic retry logic with exponential backoff
   - Rate limiting respect (handles 429 responses)
   - Progress tracking and statistics

4. **Data Organization** (`models.py`):
   - Structured data models using Python dataclasses
   - Consistent data validation and cleaning
   - Easy conversion to pandas DataFrame

## Output

The scraper generates several files:

- `database\data\quintoandar_{BAIRRO}_{datestamp}.csv`: Main results file
- `database\urls\urls_{BAIRRO}_{datestamp}.txt`: Collected URLs (for reuse)

### CSV Output Columns

- Basic info: `url`, `status`, `title`, `address_street`
- Property details: `area`, `quartos`, `suite`, `banheiros`, `vagas`, `andar`
- Features: `pet`, `mobiliado`, `metro_proximo`
- Prices: `Aluguel`, `Condomínio`, `IPTU`, `Seguro incêndio`, `Taxa de serviço`, `Total`

## Troubleshooting

### Common Issues

1. **No URLs Collected**:
   - Check if the neighborhood name is correct in `config.py`
   - Verify internet connection
   - Try running with `HEADLESS = False` to see browser behavior

2. **Address Extraction Failing**:
   - The scraper uses multiple fallback strategies
   - Check logs for specific parsing errors
   - Some properties may legitimately not have detailed addresses

3. **Rate Limiting**:
   - Reduce `CONCURRENCY` in `config.py`
   - Increase `RATE_LIMIT_DELAY`
   - The scraper automatically handles 429 responses

4. **Selenium Issues**:
   - Ensure Chrome browser is installed
   - Try updating ChromeDriver
   - Check if website structure has changed

### Debug Mode

Enable detailed logging by changing in `config.py`:

```python
LOG_LEVEL = "DEBUG"
```

## Legal Considerations

- Respect the website's robots.txt and terms of service
- Use reasonable delays between requests
- Don't overload the server with excessive concurrent requests
- Consider the ethical implications of web scraping
- This tool is for educational and research purposes
