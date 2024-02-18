import json
import logging
from typing import Dict, Any

from cast_ai.se.services.request_handle_svc import handle_request, CustomHTTPError, get_api_key_headers

logger = logging.getLogger(__name__)


# TODO: add logging
def cast_api_get(url: str, cast_api_key: str) -> Dict[str, Any]:
    headers = get_api_key_headers(cast_api_key)

    try:
        response = handle_request(url, headers, method="GET")
        return json.loads(response.content.decode('utf-8'))
    except CustomHTTPError as custom_err:
        raise custom_err


def cast_api_put(url: str, cast_api_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
    headers = get_api_key_headers(cast_api_key)
    headers["Content-Type"] = "application/json"
    try:
        response = handle_request(url, headers, json=data, method="PUT")
        return json.loads(response.content.decode('utf-8'))
    except CustomHTTPError as custom_err:
        raise custom_err


def cast_api_post(url: str, cast_api_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
    headers = get_api_key_headers(cast_api_key)
    try:
        response = handle_request(url, headers, json=data, method="POST")
        return json.loads(response.content.decode('utf-8'))
    except CustomHTTPError as custom_err:
        raise custom_err


def cast_api_delete(url: str, cast_api_key: str) -> Dict[str, Any]:
    headers = get_api_key_headers(cast_api_key)

    try:
        response = handle_request(url, headers, method="DELETE")
        return json.loads(response.content.decode('utf-8'))
    except CustomHTTPError as custom_err:
        logger.error(f"Error running Delete with url=[{url}] error=[{custom_err}]")
        # raise custom_err
