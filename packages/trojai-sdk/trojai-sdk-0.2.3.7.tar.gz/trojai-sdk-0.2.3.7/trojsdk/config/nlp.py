import typing as t
from dataclasses import dataclass
from trojsdk.config.base import BaseTrojConfig
from trojsdk.config.auth import TrojAuthConfig
from dataclasses_json import dataclass_json, DataClassJsonMixin, Undefined
from dataclasses_jsonschema import JsonSchemaMixin


"""
#TODO make support checks. Attacks and dataset should not be enforced, and an extra attribute should be added
which is an (optional) instance of a checks config (instantiated from some collection of checks Jsons).
If attacks is None, just the checks are ran. If the check config is None, the attacks must not be None and then
just the attacks are ran. If both are not None, the checks and the attacks are ran, with a special option of
adversarial checks which are special in that they take in the results of the attacks and return checks results.
"""

ALLOWED_SUBTASKS = tuple(["classification"])


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class NLPTrojConfig(BaseTrojConfig, DataClassJsonMixin, JsonSchemaMixin):

    """
    NLP-specific config class to hold info about the users run (including dataset and model).
    Inherits from base class and JSON dataclass.
    """

    test_run_name: str
    task_type: str
    subtask: t.Literal[ALLOWED_SUBTASKS] = "classification"
    audit: bool = False

    test_dataset: t.Optional[t.Any] = None
    train_dataset: t.Optional[t.Any] = None
    deploy_dataset: t.Optional[t.Any] = None

    model: t.Optional[t.Any] = None

    attacks: t.Union[t.List[dict], t.List[t.Any], None] = None
    integrity_checks: t.Optional[t.List[t.Union[t.Dict[str, t.Any], str]]] = None

    random_seed: t.Optional[int] = None
    num_batches_to_run: t.Optional[int] = None
    compute_severity: t.Optional[bool] = True

    custom_check: t.Optional[str] = None
    custom_evaluator_function: t.Optional[str] = None
    custom_evaluator_args: t.Optional[dict] = None
    custom_attacks: t.Optional[t.Any] = None
    save_path: t.Union[str, None] = None

    auth_config: TrojAuthConfig = None
