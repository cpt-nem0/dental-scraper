from typing import Optional

from pydantic import BaseModel


class ScrapeSettings(BaseModel):
    max_pages: Optional[int] = None
    proxies: Optional[str] = None
    export_json: Optional[str] = None


class ScrapeResponse(BaseModel):
    status: str
