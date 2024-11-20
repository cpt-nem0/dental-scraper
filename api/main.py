import multiprocessing

from fastapi import Depends, FastAPI
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from api.auth import verify_auth_token
from api.models import ScrapeResponse, ScrapeSettings
from scraper.spiders.dental_scraper import DentalCrawler

app = FastAPI(title="Med Scraper")


def run_spider(project_settings, max_pages, proxies, websocket_uri):
    process = CrawlerProcess(project_settings)
    process.crawl(
        DentalCrawler,
        max_pages=max_pages,
        proxies=proxies,
        notify_websocket_uri=websocket_uri,
    )
    process.start()


@app.post(
    "/scrape",
    response_model=ScrapeResponse,
    dependencies=[Depends(verify_auth_token)],
)
async def scrape(request: ScrapeSettings):

    project_settings = get_project_settings()
    if request.export_json:
        project_settings.set("JSON_FILENAME", request.export_json.replace(".json", ""))

    websocket_uri = "ws://127.0.0.1:8123/notify"

    p = multiprocessing.Process(
        target=run_spider,
        args=(project_settings, request.max_pages, request.proxies, websocket_uri),
    )
    p.start()
    p.join()

    return ScrapeResponse(status="crawler started!")
