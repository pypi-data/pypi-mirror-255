from urllib.parse import urlparse, urlunparse
from pydantic import validate_call

@validate_call
def remove_query_params(url: str) -> str:
    parsed_url = urlparse(url)
    clean_url = parsed_url._replace(query="")
    return urlunparse(clean_url)