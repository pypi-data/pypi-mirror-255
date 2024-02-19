from pydantic import validate_call
from typing import Optional
import httpx

from ..utils.product_url import extract_product_id_from_url
from ..settings import DEFAULT_LANGUAGE, DEFAULT_CURRENCY

class ProductFetcher:
    _params = {
        "fields": "installment",
        "minPriceCurrency": DEFAULT_CURRENCY,
        "minPrice": "100"
    }

    _headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    @validate_call
    def __init__(
        self,
        *,
        origin_url: str = f"https://{DEFAULT_LANGUAGE}.aliexpress.com",
        id: Optional[str] = None,
        url: Optional[str] = None
    ) -> None:
        if id is None and url is None:
            raise Exception("You must pass at least the `id` or `url` as an argument!")

        self._origin_url = origin_url
        self._url = f"{origin_url}/aeglodetailweb/api/store/header"

        if url:
            self._id = extract_product_id_from_url(url)
            
        else:
            self._id = id
        
    def _configure_headers(self) -> None:
        self._params["itemId"] = self._id
        self._headers["Referer"] = f"{self._origin_url}/item/{self._id}.html"

    def fetch(self) -> dict:
        self._configure_headers()
        
        response = httpx.get(
            url = self._url,
            headers = self._headers,
            params = self._params
        )

        data = response.json()

        return data