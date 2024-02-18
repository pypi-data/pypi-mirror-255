from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from predibase._errors import PredibaseError
from predibase.resource.llm.interface import _LLMDeployment, LLMDeployment, LLMDeploymentJob

if TYPE_CHECKING:
    from predibase import Predibase


class Deployment:
    def __init__(
        self,
        client: Predibase,
        name: str,
    ):
        self._client = client
        self._session = client._session

        self.name = name


class DedicatedDeployment(Deployment):
    pass


class DedicatedLLMDeployment(DedicatedDeployment):
    def _refresh(self) -> LLMDeployment:
        data = _LLMDeployment.from_dict(self._session.get_json(f"/llms/{self.name}"))
        return LLMDeployment(self._session, self.name, deployment_metadata=data)

    def is_ready(self) -> bool:
        deployment = self._refresh()
        return deployment.is_ready()

    def wait_ready(self, timeout: int = 1500) -> "DedicatedLLMDeployment":
        deployment = self._refresh()
        status = deployment.data.deployment_status.lower()

        if status == "active":
            return self

        if status in ("terminating", "canceled", "inactive", "failed"):
            raise PredibaseError(f"deployment {self.name} is in a {status} state and will not become ready")

        if status in ("queued", "initializing", "updating"):
            _ = LLMDeploymentJob(self.name, self._session).get()
            return self

    @functools.cached_property
    def model_name(self) -> str:
        deployment = self._refresh()
        return deployment.data.model_name


class ServerlessDeployment(Deployment):
    pass


class ServerlessLLMDeployment(ServerlessDeployment):
    def _refresh(self) -> LLMDeployment:
        data = _LLMDeployment.from_dict(self._session.get_json(f"/llms/{self.name}"))
        return LLMDeployment(self._session, self.name, deployment_metadata=data)

    def is_ready(self) -> bool:
        deployment = self._refresh()
        return deployment.is_ready()

    def wait_ready(self, timeout: int = 1500) -> "ServerlessLLMDeployment":
        deployment = self._refresh()
        status = deployment.data.deployment_status.lower()

        if status == "active":
            if not deployment.wait_for_ready(timeout_seconds=timeout):
                raise PredibaseError(f"deployment {self.name} did not become ready within the {timeout} second timeout")

        if status in ("terminating", "canceled", "inactive", "failed"):
            raise PredibaseError(f"deployment {self.name} is in a {status} state and will not become ready")

        if status in ("queued", "initializing", "updating"):
            _ = LLMDeploymentJob(self.name, self._session).get()
            return self

    @functools.cached_property
    def model_name(self) -> str:
        deployment = self._refresh()
        return deployment.data.model_name
