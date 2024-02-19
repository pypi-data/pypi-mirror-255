from pydantic import validate_call
import re

from .urls import remove_query_params

@validate_call
def extract_ids_from_url(url: str) -> tuple[str, str]:
    url = remove_query_params(url)

    match = re.search(r"i\.(\d+)\.(\d+)", url)

    if match is None:
        raise Exception(f"Could not get product id and shop id from url '{url}'!")

    shop_id = match.group(1)
    product_id = match.group(2)

    return shop_id, product_id