from __future__ import annotations

from predibase.pql import Session
from predibase.resource.model import create_model_repo, ModelRepo


class Repos:
    def __init__(self, session: Session):
        self._session = session

    def create(self, name: str, description: str | None = None, exists_ok: bool = False) -> ModelRepo:
        return create_model_repo(
            self._session,
            name,
            description,
            engine=None,
            exists_ok=exists_ok,
        )
