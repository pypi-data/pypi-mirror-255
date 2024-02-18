import logging

import requests
from typing import Dict, Any

# Set up logger
logger = logging.getLogger(__name__)


class CustomHTTPError(Exception):
    def __init__(self, message="HTTP Error", response=None):
        super().__init__(message)
        self.response = response


def handle_request(url: str, headers: dict, method: str, json: Dict[str, Any] = None) -> requests.Response:
    logger.debug(f"Issuing a {method} request to {url}")
    response = None
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=json)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers)
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            raise ValueError(f"Unsupported HTTP method: {method}")
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error: {errh}")
        raise CustomHTTPError(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Error Connecting: {errc}")
        raise CustomHTTPError(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout Error: {errt}")
        raise CustomHTTPError(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logger.error(f"Something went wrong: {err}")
        raise CustomHTTPError(f"Something went wrong: {err}")


def get_api_key_headers(cast_api_key: str) -> Dict[str, str]:
    api_key = cast_api_key

    if not api_key:

        raise ValueError("The cast.ai api token was not provide - most likely missing in configuration")
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "X-API-Key": api_key
    }
    return headers
