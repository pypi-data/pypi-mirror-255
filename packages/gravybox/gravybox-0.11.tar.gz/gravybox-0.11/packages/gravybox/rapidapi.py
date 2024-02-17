import os

import requests

from gravybox.betterstack import collect_logger

logger = collect_logger()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_TIMEOUT = 42


def query_rapidapi(url, host, query, extra_headers=None):
    """
    submits a query to rapidapi and
    returns a tuple: status_code, content
    raises any request related exceptions
    """
    logger.info("( ) querying rapidapi", extra={"url": url})
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": host
    }
    if extra_headers is not None:
        headers |= extra_headers
    response = requests.get(url, headers=headers, params=query, timeout=RAPIDAPI_TIMEOUT)
    if response.status_code == 200:
        content = response.json()
        logger.info("(*) queried rapidapi", extra={"status_code": response.status_code})
        return 200, content
    else:
        logger.warning("rapidapi response status code not 200",
                       extra={"status_code": response.status_code,
                              "payload": response.text})
        return response.status_code, response.text
