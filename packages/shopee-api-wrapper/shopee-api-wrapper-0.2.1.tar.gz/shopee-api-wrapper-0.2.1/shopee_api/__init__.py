from pydantic import validate_call
from typing import Optional
import httpx

from .utils.product_url import extract_ids_from_url
from .settings import DEFAULT_ORIGIN_URL

class Shopee:
    @validate_call
    def __init__(
        self,
        origin_url = DEFAULT_ORIGIN_URL
    ) -> None:
        self._origin_url = origin_url.removesuffix("/")

    @validate_call
    def fetch_product(
        self,
        *,
        url: Optional[str] = None,
        item_id: Optional[str] = None,
        shop_id: Optional[str] = None
    ) -> dict:
        if (
            url is None and
            item_id is None and
            shop_id is None
        ):
            raise Exception("You must at least pass the URL of the product or its id and the shop!")

        if url is None:
            if item_id is None or shop_id is None:
                raise Exception("You must at least pass the URL of the product or its id and the shop!")

        else:
            shop_id, item_id = extract_ids_from_url(url)

        url = f"{self._origin_url}/api/v4/pdp/get_pc"

        headers = {
            "x-api-source": "pc",
            "af-ac-enc-dat": "null"
        }

        params = {
            "shop_id": shop_id,
            "item_id": item_id
        }

        response = httpx.get(
            url = url,
            params = params,
            headers = headers
        )

        data = response.json()

        return data