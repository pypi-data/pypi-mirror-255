import json
from typing import Any, Callable, TypeVar, Union, cast
from urllib.parse import urljoin

import click
import requests
from loguru import logger

T = TypeVar("T")


class GableClient:
    def __init__(self, endpoint: str, api_key: str) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.ui_endpoint = endpoint.replace("api-", "", 1)

    def validate_api_key(self):
        if not self.api_key:
            raise click.ClickException(
                "API Key is not set. Use the --api-key argument or set GABLE_API_KEY "
                "environment variable."
            )

    def validate_endpoint(self):
        if not self.endpoint:
            raise click.ClickException(
                "API Endpoint is not set. Use the --endpoint or set GABLE_API_ENDPOINT "
                "environment variable."
            )

    def get(
        self, path: str, **kwargs: Any
    ) -> tuple[Union[list[Any], dict[str, Any]], bool, int]:
        return self._request(path, method="GET", **kwargs)

    def post(
        self, path: str, **kwargs: Any
    ) -> tuple[Union[list[Any], dict[str, Any]], bool, int]:
        return self._request(path, method="POST", **kwargs)

    def _request(
        self,
        path: str,
        method: str = "GET",
        log_payload_filter: Callable = lambda json_payload: json_payload,
        **kwargs: Any,
    ) -> tuple[Union[list[Any], dict[str, Any]], bool, int]:
        self.validate_api_key()
        self.validate_endpoint()
        url = urljoin(self.endpoint, path)

        # Filter the JSON payload to remove spammy/secret request data
        kwargs_copy = json.loads(json.dumps(kwargs))
        if "json" in kwargs_copy:
            kwargs_copy["json"] = log_payload_filter(kwargs_copy["json"])

        logger.debug(f"{method} {url}: {kwargs_copy}")

        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

        if method.upper() == "GET":
            response = requests.get(url, headers=headers, **kwargs)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, **kwargs)
        else:
            raise click.ClickException("Invalid HTTP method: {method} not supported.")

        # Log the response
        logger.debug(
            f"{'OK' if response.ok else 'ERROR'} ({response.status_code}): {response.text}"
        )

        # Check for missing api key
        if response.status_code == 403:
            raise click.ClickException("Invalid API Key")

        # Try parsing the response as JSON
        try:
            parsed_response = response.json()
        except:
            raise click.ClickException(
                f"Unable to parse server response as JSON: {response.text}"
            )

        return (
            cast(dict[str, Any], parsed_response),
            response.status_code == 200,
            response.status_code,
        )
