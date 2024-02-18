from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, Any

from predibase._errors import PredibaseError
from predibase.resource.model import ModelFuture
from predibase.resource_util import build_model

if TYPE_CHECKING:
    from predibase import Predibase


logger = logging.getLogger(__name__)


class Model:
    pass


class LLM(Model):
    pass


class PretrainedLLM(LLM):
    pass


class PretrainedHuggingFaceLLM(PretrainedLLM):
    def __init__(self, name: str):
        # TODO: check the validity of the provided name via HuggingFace
        self.name = name
        if self.name.startswith("hf://"):
            self.name = self.name[len("hf://") :]


class FinetunedLLM(LLM):
    pass


class FinetunedLLMAdapter(FinetunedLLM):
    # TODO: accept version instead
    def __init__(self, client: Predibase, repo_name: str, model_id: int):
        self._model_id = model_id
        self._client = client
        self._session = client._session  # Directly using the session in the short term as we transition to v2.
        self._repo_name = repo_name

        self._refresh()

    def _refresh(self):
        endpoint = f"/models/version/{self._model_id}"
        resp = self._session.get_json(endpoint)
        self._model = build_model(resp["modelVersion"], self._session)

    @property
    def uri(self) -> str:
        return f"pb://models/{self._repo_name}/{self._model_id}"

    @property
    def train_config(self) -> Dict:
        return self._model.config

    @property
    def base_model_name(self) -> str:
        return self._model.llm_base_model_name  # Should never be None for an adapter.

    def wait_ready(self, show_tensorboard: bool = False) -> FinetunedLLMAdapter:
        self._refresh()
        status = self._model.status

        if status in ("ready", "deploying", "deployed", "undeploying"):
            return self

        if status == "canceled":
            raise PredibaseError(f"model {self._model_id} was canceled")

        if status == "failed":
            raise PredibaseError(f"model {self._model_id} failed to train: {self._model.error_text}")

        _ = ModelFuture(self._model_id, self._session).get(launch_tensorboard=show_tensorboard)
        return self
