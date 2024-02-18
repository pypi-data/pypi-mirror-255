import os

import requests

from gravybox.betterstack import collect_logger
from gravybox.exceptions import BadStatusCode

logger = collect_logger()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_TIMEOUT = 42


def query_rapidapi(upstream_api, url, host, query, extra_headers=None):
    """
    submits a query to rapidapi and
    returns a tuple: status_code, content
    raises any request related exceptions
    """
    logger.info("querying rapidapi", extra={"query": query, "upstream_api": upstream_api})
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": host
    }
    if extra_headers is not None:
        headers |= extra_headers
    response = requests.get(url, headers=headers, params=query, timeout=RAPIDAPI_TIMEOUT)
    if response.status_code == 200:
        return response.json()
    else:
        raise BadStatusCode(query, upstream_api, response)
