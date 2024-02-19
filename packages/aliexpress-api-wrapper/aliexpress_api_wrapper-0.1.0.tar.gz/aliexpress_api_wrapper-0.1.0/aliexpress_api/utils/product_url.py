from pydantic import validate_call
import re

from .urls import remove_query_params

@validate_call
def extract_product_id_from_url(url: str) -> str:
    match = re.search(r"/(\d+)\.html$", remove_query_params(url))

    if match is None:
        raise Exception(f"Could not get url id '{url}'!")

    id = match.group(1)
    
    return id