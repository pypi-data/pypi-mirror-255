import logging
import os
import platform
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import requests

from predibase._errors import PredibaseError, warn_outdated_sdk
from predibase.pql import start_session
from predibase.resource.user import User
from predibase.resources.adapters import Adapters
from predibase.resources.completions import Completions
from predibase.resources.datasets import Datasets
from predibase.resources.deployments import Deployments
from predibase.resources.models import Models
from predibase.resources.repos import Repos
from predibase.util.settings import load_settings
from predibase.version import __version__

_DEFAULT_API_GATEWAY = "https://api.app.predibase.com/v1"
_DEFAULT_SERVING_ENDPOINT = "serving.app.predibase.com"


logger = logging.getLogger(__name__)


class Predibase:
    def __init__(
        self,
        *,
        api_token: Optional[str] = None,
    ):
        """
        Create a new Predibase client instance.

        If not provided, optional params will be set by, in order of precedence:
        * Current environment variables
        * Hard-coded defaults

        :param api_token: The authentication token for the Predibase API.
        """
        api_token = api_token or os.environ.get("PREDIBASE_API_TOKEN") or load_settings().get("token")
        api_gateway = os.environ.get("PREDIBASE_GATEWAY") or _DEFAULT_API_GATEWAY
        serving_endpoint = os.environ.get("PREDIBASE_SERVING_ENDPOINT") or _DEFAULT_SERVING_ENDPOINT

        if not api_token:
            raise PredibaseError(
                "An api_token must either be explicitly provided or set via the PREDIBASE_API_TOKEN "
                "environment variable."
            )

        if not api_gateway:
            raise PredibaseError("PREDIBASE_GATEWAY cannot be empty.")

        if not api_gateway.startswith("https://"):
            logger.info(
                f"No HTTP scheme provided for PREDIBASE_GATEWAY (got: {api_gateway}), defaulting to `https://`."
            )
            api_gateway = f"https://{api_gateway}"

        if not serving_endpoint:
            raise PredibaseError("PREDIBASE_SERVING_ENDPOINT cannot be empty.")

        self.api_token = api_token
        self.api_gateway = api_gateway
        self.serving_http_endpoint = serving_endpoint

        self._session = start_session(self.api_gateway, self.api_token, self.serving_http_endpoint)

        self.adapters = Adapters(self)
        self.completions = Completions(self)
        self.datasets = Datasets(self._session)
        self.deployments = Deployments(self)
        self.models = Models(self._session)
        self.repos = Repos(self._session)

    @property
    def default_headers(self) -> Dict[str, str]:
        return {
            "Authorization": "Bearer " + self.api_token,
            "User-Agent": f"predibase-sdk/{__version__} ({platform.version()})",
        }

    def _get_current_user(self):
        resp = self.get_json("/users/current")
        return User.from_dict(resp)

    @warn_outdated_sdk
    def _get(self, endpoint: str, params: dict = None):
        return self._http.get(urljoin(self.api_gateway, endpoint), headers=self.default_headers, params=params)

    @warn_outdated_sdk
    def _post(self, endpoint: str, data: Optional[Any] = None, json: Optional[Any] = None, **kwargs):
        return self._http.post(
            urljoin(self.api_gateway, endpoint), data=data, json=json, headers=self.default_headers, **kwargs
        )

    @warn_outdated_sdk
    def _delete(self, endpoint: str):
        return self._http.delete(urljoin(self.api_gateway, endpoint), headers=self.default_headers)

    @warn_outdated_sdk
    def _put(self, endpoint: str, json: Optional[Any]):
        return self._http.put(urljoin(self.api_gateway, endpoint), json=json, headers=self.default_headers)

    @warn_outdated_sdk
    def _get_serving(self, endpoint: str):
        return self._http.get(urljoin(self.serving_http_endpoint, endpoint), headers=self.default_headers)

    @warn_outdated_sdk
    def _post_serving(self, endpoint: str, data: Optional[Any] = None, json: Optional[Any] = None, **kwargs):
        return self._http.post(
            urljoin(self.serving_http_endpoint, endpoint),
            data=data,
            json=json,
            headers=self.default_headers,
            **kwargs,
        )

    @warn_outdated_sdk
    def _get_ws(self, endpoint: str):
        ws_url = self.api_gateway.replace("https://", "wss://").replace("http://", "ws://")
        return requests.Session().get(ws_url + endpoint, headers=self.default_headers, timeout=None, stream=True)

    def _format_url(self, endpoint: str) -> str:
        if "localhost" in self.api_gateway:
            root_url = "http://localhost:8000"
        else:
            url = self.api_gateway
            if "api." in url:
                url = url.replace("api.", "").replace("/v1", "")
            root_url = url

        from urllib.parse import urljoin

        return urljoin(root_url, endpoint)
