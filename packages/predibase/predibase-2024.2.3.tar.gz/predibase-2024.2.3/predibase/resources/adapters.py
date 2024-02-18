from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Dict, Tuple

import yaml
from tabulate import tabulate

from predibase._errors import PredibaseError
from predibase.resource.llm.prompt import PromptTemplate
from predibase.resources.model import PretrainedHuggingFaceLLM, FinetunedLLMAdapter
from predibase.util import log_info, get_url

if TYPE_CHECKING:
    from predibase import Predibase
    from predibase.resources.dataset import Dataset
    from predibase.resources.repo import Repo


_PATH_HERE = os.path.abspath(os.path.dirname(__file__))
_TEMPLATE_DIR = os.path.join(_PATH_HERE, "../resource/llm/templates")
_CONFIG_FILENAME = "config.yaml"  # Name of config file for loading templates.


class Adapters:
    def __init__(self, client: Predibase):
        self._client = client
        self._session = client._session  # Directly using the session in the short term as we transition to v2.

    def create(
        self,
        config: FinetuneConfig,
        *,
        description: str | None = None,
        repo: str | Repo | None = None,
        wait: bool = True,
        show_tensorboard: bool = True,
    ):
        # TODO(jeff): docstring

        if show_tensorboard and not wait:
            raise RuntimeError("`show_tensorboard` is a blocking option and thus requires `wait` to be True.")

        if repo is None:
            # If no repo is specified, automatically construct the repo name from the dataset and model name.
            dataset_name = config.dataset.name
            if "/" in dataset_name:
                _, dataset_name = dataset_name.split("/")

            model_name = config.base_model.name
            if "/" in model_name:
                _, model_name = model_name.split("/")

            repo = f"{model_name}-{dataset_name}"

        if isinstance(repo, str):
            if "/" in repo:
                repo = repo.replace("/", "-")
            repo = self._client.repos.create(repo, exists_ok=True)

        train_req = {
            "config": config.render(),
            "datasetID": config.dataset.id,
            "repoID": repo.id,
            "description": description,
        }

        resp = self._session.post_json("/models/train", train_req)
        model_id = resp["model"]["id"]

        # Output link to UI model page
        endpoint = f"models/version/{model_id}"
        url = get_url(self._session, endpoint)
        log_info(f"Check Status of Model Training Here: [link={url}]{url}")

        adapter = FinetunedLLMAdapter(self._client, repo.name, model_id)
        if wait:
            return adapter.wait_ready(show_tensorboard=show_tensorboard)
        return adapter

    @staticmethod
    def FinetuneConfig(*args, **kwargs) -> FinetuneConfig:
        return FinetuneConfig(*args, **kwargs)

    def get(self, adapter_uri: str) -> FinetunedLLMAdapter:
        if adapter_uri.startswith("pb://adapters/"):
            adapter_uri = adapter_uri[len("pb://adapters/") :]

        tokens = adapter_uri.split("/")
        if len(tokens) < 2:
            raise PredibaseError(f"expected a URI of the form [pb://adapters/]<repo_name>/<version>")

        resp = self._session.get_json(f"/models/version/name/{tokens[0]}?version={tokens[1]}")
        if not resp.get("llmBaseModelName", ""):
            raise PredibaseError(f"uri {adapter_uri} does not point to a fine-tuned LLM adapter")

        return FinetunedLLMAdapter(self._client, tokens[0], resp["id"])


class FinetuneConfig:
    def __init__(
        self,
        *,
        base_model: str | PretrainedHuggingFaceLLM,
        dataset: Dataset,  # TODO: enable passing dataset by name once we get rid of connection namespacing
        prompt_template: str | PromptTemplate,
        target: str,
        finetune_template: FinetuneTemplate | None = None,
        epochs: int | None = None,
        train_steps: int | None = None,
        learning_rate: float | None = None,
    ):

        if train_steps is not None and epochs is not None:
            raise ValueError("Cannot specify both train_steps and epochs.")

        self._base_model = base_model
        if isinstance(self._base_model, str):
            self._base_model = PretrainedHuggingFaceLLM(self._base_model)

        self._dataset = dataset
        self._prompt_template = prompt_template
        self._target = target
        self._finetune_template = finetune_template or FinetuneTemplateCollection().default
        self._epochs = epochs
        self._train_steps = train_steps
        self._learning_rate = learning_rate

    @property
    def base_model(self) -> PretrainedHuggingFaceLLM:
        return self._base_model

    @property
    def dataset(self) -> Dataset:
        return self._dataset

    def render(self) -> Dict:
        prompt_template = self._prompt_template
        if isinstance(prompt_template, PromptTemplate):
            prompt_template = prompt_template.render()

        config = self._finetune_template.to_config(self._base_model, prompt_template, self._target)

        # HACK(Arnav): Temporary hack to inject the right target_modules into the config for mixtral and
        # mixtral instruct. This should be removed once the Mixtral models have a default PEFT mapping for LoRA
        # target_modules. See MLX-1680: https://linear.app/predibase/issue/MLX-1680/remove-peftlora-mixtral-hack-in-the-predibase-sdk # noqa
        if (
            config.get("base_model", "") in {"mistralai/Mixtral-8x7B-v0.1", "mistralai/Mixtral-8x7B-Instruct-v0.1"}
            and "adapter" in config
            and config.get("adapter", {}).get("target_modules", None) is None
        ):
            config["adapter"]["target_modules"] = ["q_proj", "v_proj"]

        # Apply first-class training parameters.
        if self._train_steps is not None:
            config["trainer"]["train_steps"] = self._train_steps
        if self._epochs is not None:
            config["trainer"]["epochs"] = self._epochs
        if self._learning_rate is not None:
            config["trainer"]["learning_rate"] = self._learning_rate

        return config


class FinetuneTemplateCollection(dict):
    def __init__(self):
        super().__init__()

        for filename in os.listdir(_TEMPLATE_DIR):
            if not filename.endswith(".yaml"):
                continue

            if filename == _CONFIG_FILENAME:
                with open(os.path.join(_TEMPLATE_DIR, _CONFIG_FILENAME)) as config_file:
                    self._config = yaml.safe_load(config_file)
            else:
                tmpl = FinetuneTemplate(filename=os.path.join(_TEMPLATE_DIR, filename))
                self[tmpl.name] = tmpl

    @property
    def default(self) -> FinetuneTemplate:
        default_name = self._config.get("default", "")
        tmpl = self.get(default_name, None)
        if tmpl is None:
            raise RuntimeError(f"the default template '{default_name}' was not found")

        return tmpl

    def compare(self):
        print(self)

    def __str__(self):
        def make_row(key) -> Tuple[str, str, str]:
            tmpl = self[key]
            default_indicator = "------>" if tmpl.name == self._config["default"] else ""
            return default_indicator, key, tmpl.description

        return tabulate(
            (make_row(k) for k in sorted(self.keys())),
            tablefmt="simple_grid",
            headers=["Default", "Name", "Description"],
            colalign=["center"],
        )


@dataclass
class FinetuneTemplate:
    filename: str
    _meta: Optional[dict] = field(default=None, init=False)
    _raw_template_str: Optional[str] = field(default=None, init=False)

    @property
    def name(self) -> str:
        if self._meta is None:
            self._load()
        return self._meta["name"]

    @property
    def description(self) -> str:
        if self._meta is None:
            self._load()
        return self._meta["description"]

    def to_config(
        self,
        model: str | PretrainedHuggingFaceLLM,
        prompt_template: str = "__PROMPT_TEMPLATE_PLACEHOLDER__",
        target: str = "__TARGET_PLACEHOLDER__",
    ) -> dict:
        if self._raw_template_str is None:
            self._load()

        if isinstance(model, PretrainedHuggingFaceLLM):
            model = model.name

        cfg = yaml.safe_load(
            self._raw_template_str.format(
                base_model=model,
                prompt_template=prompt_template,
                target=target,
            ),
        )
        del cfg["template_meta"]
        return cfg

    def _load(self):
        with open(os.path.join(_TEMPLATE_DIR, self.filename)) as f:
            self._raw_template_str = f.read()

        self._meta = yaml.safe_load(self._raw_template_str)["template_meta"]
