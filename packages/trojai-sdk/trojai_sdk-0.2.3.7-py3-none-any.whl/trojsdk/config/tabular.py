"""Central "hub" class to hold all info about user's run on tabular models"""


from dataclasses import dataclass
from dataclasses_jsonschema import JsonSchemaMixin
from trojsdk.config.base import BaseTrojConfig
from trojsdk.config.auth import TrojAuthConfig
from trojsdk.core.troj_error import TrojConfigError
from typing import Any, Union, Optional, Literal, List, Dict
from dataclasses_json import dataclass_json, DataClassJsonMixin, Undefined


ALLOWED_SUBTASKS = tuple(["classification", "regression"])


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class TabularTrojConfig(BaseTrojConfig, DataClassJsonMixin, JsonSchemaMixin):

    """Tabular config class. Stores all relevant info about the user's run"""

    test_run_name: str
    task_type: str
    subtask: Literal[ALLOWED_SUBTASKS] = "classification"
    audit: Union[bool, dict] = False
    run_attacks_from_model_profile: bool = False

    test_dataset: Optional[Any] = None
    train_dataset: Optional[Any] = None
    deploy_dataset: Optional[Any] = None

    model: Optional[Any] = None

    attacks: Union[List[dict], List[Any], None] = None
    integrity_checks: Optional[List[Union[Dict[str, Any], str]]] = None

    random_seed: Optional[int] = None
    num_batches_to_run: Optional[int] = None

    custom_check: Optional[str] = None
    custom_evaluator_function: Optional[str] = None
    custom_evaluator_args: Optional[str] = None

    save_path: Union[str, None] = None
    auth_config: Union[TrojAuthConfig, None] = None

    def __post_init__(self):
        self.task_type = "tabular"

        if self.subtask not in ALLOWED_SUBTASKS:
            raise TrojConfigError(
                f"Subtask {self.subtask} is not supported yet. "
                f"Currently supported subtasks are: {ALLOWED_SUBTASKS}"
            )

    def get_schema(self):
        """
        Functionality from JsonSchemaMixin.
        Dump attributes of self as a json schema

        :return:
        """

        return self.json_schema()
