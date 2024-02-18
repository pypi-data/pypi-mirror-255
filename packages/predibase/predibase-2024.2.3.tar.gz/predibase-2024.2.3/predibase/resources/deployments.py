from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from predibase._errors import PredibaseError
from predibase.resource.llm import interface
from predibase.resource.llm.interface import _LLMDeployment
from predibase.resources.model import FinetunedLLMAdapter, PretrainedHuggingFaceLLM

if TYPE_CHECKING:
    from predibase import Predibase

from predibase.resources.deployment import Deployment, ServerlessLLMDeployment, DedicatedLLMDeployment


class Deployments:
    def __init__(self, client: Predibase):
        self._client = client
        self._session = client._session

    def get(self, deployment_name: str) -> Deployment:
        # No need to provide the full old-style URI here since we know we're dealing with a Predibase deployment.
        if deployment_name.startswith("pb://deployments/"):
            deployment_name = deployment_name[len("pb://deployments/") :]
        if deployment_name.startswith("pb://"):
            deployment_name = deployment_name[len("pb://") :]

        # TODO: for now relying on the old payload and dataclass.
        data = _LLMDeployment.from_dict(self._session.get_json(f"/llms/{deployment_name}"))
        if data.is_shared:
            return ServerlessLLMDeployment(self._client, deployment_name)
        else:
            return DedicatedLLMDeployment(self._client, deployment_name)

    def create(
        self,
        name: str,
        model: FinetunedLLMAdapter | PretrainedHuggingFaceLLM,
        *,
        hf_token: str | None = None,
        auto_suspend_seconds: int | None = None,
        max_input_length: int | None = None,
        max_total_tokens: int | None = None,
        max_batch_prefill_tokens: int | None = None,
        quantization_kwargs: Dict[str, str] | None = None,
        revision: str | None = None,
        overwrite: bool | None = False,
        wait: bool = True,
    ) -> DedicatedLLMDeployment:
        if isinstance(model, FinetunedLLMAdapter):
            job = interface.deploy_llm(
                session=self._session,
                deployment_name=name,
                hf_token=hf_token,
                auto_suspend_seconds=auto_suspend_seconds,
                max_input_length=max_input_length,
                max_total_tokens=max_total_tokens,
                max_batch_prefill_tokens=max_batch_prefill_tokens,
                quantization_kwargs=quantization_kwargs,
                revision=revision,
                predibase_model_uri=model.uri,
                overwrite=overwrite,
            )
        elif isinstance(model, PretrainedHuggingFaceLLM):
            job = interface.deploy_llm(
                session=self._session,
                deployment_name=name,
                hf_token=hf_token,
                auto_suspend_seconds=auto_suspend_seconds,
                max_input_length=max_input_length,
                max_total_tokens=max_total_tokens,
                max_batch_prefill_tokens=max_batch_prefill_tokens,
                quantization_kwargs=quantization_kwargs,
                revision=revision,
                huggingface_model_name=model.name,
                overwrite=overwrite,
            )
        else:
            raise PredibaseError(f"unable to deploy unexpected model type {model.__class__}")

        deployment = DedicatedLLMDeployment(self._client, name)
        if wait:
            deployment.wait_ready()

        return deployment

    def delete(self, deployment: str | DedicatedLLMDeployment):
        if isinstance(deployment, str):
            deployment = DedicatedLLMDeployment(self._client, deployment)

        dep = deployment._refresh()
        if dep.data.is_shared():
            raise PredibaseError(f"cannot delete shared deployment {dep.name}")

        dep.delete()
