# Web Scraping Project Documentation

## Overview
This project consists of a FastAPI-based API service and a Scrapy spider designed to scrape dental product information. The system features two main APIs:
1. A REST API for initiating the spider (Bearer token protected)
2. A WebSocket endpoint for receiving scraping completion notifications

## Project Structure
```
.
├── api/                  # FastAPI application
│   ├── auth.py          # Authentication logic
│   ├── main.py          # Main API endpoints
│   ├── models.py        # Pydantic models
│   └── websocket.py     # WebSocket handling
├── scraper/             # Scrapy spider
│   ├── items.py         # Item definitions
│   ├── pipelines.py     # Data processing pipelines
│   ├── settings.py      # Scrapy settings
│   └── spiders/
│       └── dental_scraper.py  # Main spider
└── data/                # Data storage
```

## API Documentation

### Spider API

#### Authentication
The spider API is protected with Bearer token authentication. Include the token in your request headers:
```
Authorization: Bearer <your-token>
```

#### Endpoints

##### POST /scrape
Initiates the dental product scraping process.

**Request Body:**
```python
{
    "max_pages": 10,        # Optional: Maximum pages to scrape
    "proxies": "...",       # Optional: Proxy configuration
    "export_json": "..."    # Optional: JSON export file name path
}
```

**Response:**
```python
{
    "status": "started"     # Status of the scraping job
}
```

### WebSocket API

#### Connection
Connect to the WebSocket endpoint to receive scraping completion notifications:
```
ws://<host>/notify
```

#### Message
```json
{
    "status": str,
    "total_items_scraped": int,
    "total_items_saved": int,
    "total_pages_scraped": int,
}
```


## Scraper Configuration

### Product Schema
The scraper collects the following information for each product:
```python
{
    "product_title": str,    # Title of the dental product
    "product_price": float,   # Current price
    "image_url": str         # URL or path to product image
    "local_path": str        # path of image saved on the local directory
}
```

### Pipelines

#### 1. Redis Cache Pipeline
- Caches product prices
- Prevents unnecessary database updates when prices haven't changed
- Configuration in `settings.py`:
  ```python
  ITEM_PIPELINES = {
      'scraper.pipelines.RedisCachePipeline': 300
  }
  ```

#### 2. Image Download Pipeline
- Downloads product images to local directory
- Configuration in `settings.py`:
  ```python
  ITEM_PIPELINES = {
      'scraper.pipelines.ImageDownloadPipeline': 400
  }
  ```

#### 3. JSON Export Pipeline
- Stores scraped data in JSON format
- Configurable export path through API settings
- Configuration in `settings.py`:
  ```python
  ITEM_PIPELINES = {
      'scraper.pipelines.JsonExportPipeline': 500
  }
  ```

## Setup and Installation

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Start the API server:
   ```bash
   uvicorn api.main:app --reload --port=8000
   ```

3. Start websocket:
    ```bash
    uvicorn api.websocket:app --reload --port=8123
    ```

4. For Running scraper only
    ```bash
    scrapy crawl dental_crawler -O output.json
    ```

## Error Handling

The system includes several error handling mechanisms:
- Invalid authentication tokens return 401 Unauthorized
- Spider initialization failures are reported via WebSocket
- Redis connection issues are logged and gracefully handled

## Performance Considerations

- Redis caching prevents unnecessary database updates
- Configurable page limits to control scraping scope
- Proxy support for distributed scraping
