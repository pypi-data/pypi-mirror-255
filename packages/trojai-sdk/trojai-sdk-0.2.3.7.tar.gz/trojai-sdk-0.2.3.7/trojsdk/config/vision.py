"""Central "hub" class for all info about the user's run on a Vision task"""

from dataclasses import dataclass
from typing import Any, Optional, Union, List, Literal, Dict
from trojsdk.config.base import BaseTrojConfig, BaseTrojDataset
from trojsdk.core.troj_error import TrojConfigError
from trojsdk.config.auth import TrojAuthConfig
from dataclasses_jsonschema import JsonSchemaMixin
from dataclasses_json import dataclass_json, DataClassJsonMixin, Undefined

ALLOWED_SUBTASKS = tuple(["classification", "object detection", "other"])

VISION_ATT_DICT = [
    "corruptions",
    "fgsm",
    "pgd",
    "adaptive_pgd",
    "regularized_pgd",
    "adaptive_regularized_pgd",
    "min_corruption_search",
]

VISION_ATTACK_KEYS = tuple(VISION_ATT_DICT)


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class VisionTrojConfig(BaseTrojConfig, DataClassJsonMixin, JsonSchemaMixin):

    """Vision config class. Stores all relevant info about the user's run. Inherit from base and JSON dataclass"""

    test_run_name: str
    attacks: Union[List[dict], Literal[VISION_ATTACK_KEYS]]

    test_dataset: Any
    model: Any
    task_type: str
    framework: str = None
    num_batches_to_run: Optional[int] = None
    random_seed: Optional[int] = None
    subtask: Literal[ALLOWED_SUBTASKS] = None

    custom_evaluator_function: Optional[str] = None
    custom_evaluator_args: Optional[dict] = None
    custom_attacks: Optional[Any] = None

    auth_config: TrojAuthConfig = None
    save_path: Optional[str] = None

    def __post_init__(self):
        """Let the dataset know what the framework is going to be, and create data loader with that info"""

        self.task_type = "vision"

        if self.subtask is not None:
            self.subtask = self.subtask.casefold()
            if self.subtask not in ALLOWED_SUBTASKS:
                raise TrojConfigError(
                    f'Provided subtask "{self.subtask}" not supported. '
                    f"Currently supported subtasks are: {ALLOWED_SUBTASKS}"
                )


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class VisionTrojDataset(BaseTrojDataset, DataClassJsonMixin, JsonSchemaMixin):
    """Dataset class to wrap around the user's data stored on disk. Constructed from the user's config file"""

    """
    This class is a high-level wrapper for the user's dataset.
    It holds the dataset itself and allows batching and iteration operations on
    the user's data.
    """

    name: str
    path_to_data: str
    path_to_annotations: str
    data_loader_config: dict
    data_loader: Optional[Any] = None
    metadata: Optional[Any] = None
    classes_dictionary: Optional[Union[Dict[str, int], str]] = None
    column_defs: Optional[list] = None
