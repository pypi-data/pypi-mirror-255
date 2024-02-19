from pydantic import validate_call
from urllib.parse import quote
from parsel import Selector
import httpx
import json

from ..settings import DEFAULT_LANGUAGE

class ProductSearcher:
    @validate_call
    def __init__(
        self,
        origin_url: str = f"https://{DEFAULT_LANGUAGE}.aliexpress.com"
    ) -> None:
        self._origin_url = origin_url

    @validate_call
    def _parse_data(self, fields: dict) -> dict:
        data = { "products": [] }

        products: list[dict] = fields["mods"]["itemList"]["content"]

        for product in products:
            product_data = {
                "id": product["productId"],
                "url": f"https://www.aliexpress.com/item/{product['productId']}.html",
                "type": product["productType"],
                "title": product["title"]["displayTitle"] if "title" in product else None,
                "min_price": product["prices"]["salePrice"]["minPrice"],
                "currency": product["prices"]["salePrice"]["currencyCode"],
                "trade": product.get("trade", {}).get("tradeDesc"),
                "thumbnail": product["image"]["imgUrl"].lstrip("/"),
                "store": {
                    "url": product["store"]["storeUrl"],
                    "name": product["store"]["storeName"],
                    "id": product["store"]["storeId"],
                    "member_id": product["store"]["aliMemberId"],
                }
            }

            data["products"].append(product_data)

        return data

    @validate_call
    def _parse_html(self, html: str) -> dict:

        selector = Selector(html)
        script_with_data = selector.xpath("//script[contains(text(), 'window._dida_config_._init_data_=')]")

        raw_data = json.loads(
            script_with_data.re(
                r"_init_data_\s*=\s*{\s*data:\s*({.+}) }"
            )[0]
        )

        fields = raw_data["data"]["root"]["fields"]

        return self._parse_data(fields)

    @validate_call
    def search(self, query: str, page_number: int = 1) -> dict:
        query_without_spaces = query.replace(" ", "-")
        quoted_query = quote(query)

        url = f"{self._origin_url}/w/wholesale-{query_without_spaces}.html"

        params = {
            "SearchText": quoted_query,
            "page": page_number
        }

        response = httpx.get(
            url = url,
            params = params,
            follow_redirects = True
        )

        html = response.text

        data = self._parse_html(html)

        return data