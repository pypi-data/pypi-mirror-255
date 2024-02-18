from __future__ import annotations

from predibase.pql import Session
from predibase.resources.model import PretrainedHuggingFaceLLM


class Models:
    def __init__(self, session: Session):
        self._session = session

    def from_hf(self, model_name: str) -> PretrainedHuggingFaceLLM:
        return PretrainedHuggingFaceLLM(model_name)
