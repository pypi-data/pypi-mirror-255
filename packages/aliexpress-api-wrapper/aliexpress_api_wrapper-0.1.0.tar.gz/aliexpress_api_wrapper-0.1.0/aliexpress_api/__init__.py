from pydantic import validate_call
from typing import Optional

from .settings import DEFAULT_CURRENCY, DEFAULT_LANGUAGE
from .product import ProductFetcher
from .search import ProductSearcher

class AliExpress:
    @validate_call
    def __init__(
        self,
        currency: str = DEFAULT_CURRENCY,
        language: str = DEFAULT_LANGUAGE

    ) -> None:
        self._currency = currency
        self._language = language
        self._origin_url = f"https://{language}.aliexpress.com"

    def fetch_product(
        self,
        *,
        id: Optional[str] = None,
        url: Optional[str] = None
    ) -> dict:
        fetcher = ProductFetcher(
            origin_url = self._origin_url,
            url = url,
            id = id 
        )

        data = fetcher.fetch()

        return data

    @validate_call
    def search_products(self, query: str, page_number: int = 1) -> dict:
        searcher = ProductSearcher(self._origin_url)
        data = searcher.search(query, page_number)
        return data