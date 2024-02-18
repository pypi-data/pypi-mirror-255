"""Base config class for task-specific config classes"""

import os, re, ast
from pathlib import Path
from typing import Any, Union, Optional, Dict, List
from dataclasses import dataclass
from dataclasses_jsonschema import JsonSchemaMixin
from dataclasses_json.undefined import UndefinedParameterError
from dataclasses_json import dataclass_json, DataClassJsonMixin, Undefined
from trojsdk.config.auth import TrojAuthConfig
from trojsdk.core.troj_error import TrojConfigError
from trojsdk.core import data_utils, troj_logging

log = troj_logging.getLogger(__file__)


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class BaseTrojConfig(DataClassJsonMixin, JsonSchemaMixin):

    """
    Base class for loading user top-level JSON config.
    Docker metadata is not part of any Config object. It must be popped off the config dict before a Config object is made.
    """

    test_run_name: str
    task_type: str
    attacks: Any
    test_dataset: Any
    model: Any
    auth_config: TrojAuthConfig
    docker_metadata: Optional[Dict] = None

    @classmethod
    def config_from_json(
        cls,
        json_path: Union[str, Path],
        sub_jsons: bool = True,
        auth_config: TrojAuthConfig = None,
    ) -> "BaseTrojConfig":
        """
        This method is needed to read a config dictionary from a JSON file on disk
        and assign the values from the JSON to the fields of the class by corresponding
        keys. Note that the keys in the JSON file must be exactly the same as the names
        of the class fields.

        This method through inheritance will be used to construct task-specific configs

        :param json_path: path to JSON config file (str or pathlib.Path)
        :param sub_jsons: if True, check every value in config JSON to be a path to a lower level JSON config (bool)
        :return: class with values from JSON config assigned to the class fields
        """

        if type(json_path) == str:
            json_path = Path(json_path)

        config_dict = data_utils.load_json_from_disk(json_path, sub_jsons=sub_jsons)
        return cls.config_from_dict(config_dict, auth_config)

    @classmethod
    def config_from_dict(
        cls, config_dict: dict, auth_config: TrojAuthConfig = None
    ) -> "BaseTrojConfig":
        """Given a dictionary, initializes fields with values from corresponding keys"""

        invalid_paths = data_utils.test_paths(config_dict)

        if len(invalid_paths) > 0:
            err = TrojConfigError(
                "\n\nSome paths provided were invalid!"
                + "\n"
                + "Please ensure the following paths are correct:"
                + "\n"
                + str(invalid_paths)
                + "\n\n"
                + "The current working directory is:"
                + "\n"
                + str(os.getcwd())
                + "\n\n"
                + "The following files are in the working directory:"
                + "\n"
                + str(os.listdir())
            )
            raise (err)

        try:
            if auth_config is None:
                auth_config = TrojAuthConfig.config_from_dict(
                    config_dict["auth_config"]
                )
            config_dict["auth_config"] = auth_config

            return cls.from_dict(config_dict)

        except KeyError as err:
            raise TrojConfigError(
                f'\n\nKey "{err.args[0]}" missing from json.'
                "Make sure all required key-value pairs are "
                "present in the json"
            )

        except AttributeError as e:
            log.error(e)
            raise TrojConfigError(
                "\n\nCould not unpack one of sub-jsons. Make sure "
                "that paths to sub-jsons are specified correctly."
            )

        except UndefinedParameterError as err:
            message = str(err)
            dict_substring = (
                "{" + re.findall("{(.+?)}", re.sub("\(.+?\)", "", message))[0] + "}"
            )
            unknown_dict = ast.literal_eval(dict_substring)
            raise TrojConfigError(
                f'\n\nGot unexpected key(s) in json: "{list(unknown_dict)}"\n'
            )

        except TypeError as err:
            raise TrojConfigError(
                f"\n\nInvalid auth_keys datatype; ensure auth_keys is a valid subjson"
            )

        except Exception as err:
            if hasattr(err, "message"):
                raise TrojConfigError(err.message)
            else:
                raise TrojConfigError(repr(err))


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class BaseTrojARtConfig(DataClassJsonMixin, JsonSchemaMixin):

    """
    Base class for loading user top-level JSON config.
    Docker metadata is not part of any Config object. It must be popped off the config dict before a Config object is made.
    """

    name: str
    victim_model: Any
    attacks: Any
    auth_config: TrojAuthConfig
    redteam_model: Optional[Any] = None
    moderator_model: Optional[Any] = None
    azure_safety_endpoint: Optional[Any] = None
    save_path: Optional[str] = None
    docker_metadata: Optional[Dict] = None
    k8s_metadata: Optional[Dict] = None

    @classmethod
    def config_from_json(
        cls,
        json_path: Union[str, Path],
        sub_jsons: bool = True,
        auth_config: TrojAuthConfig = None,
    ) -> "BaseTrojARtConfig":
        """
        This method is needed to read a config dictionary from a JSON file on disk
        and assign the values from the JSON to the fields of the class by corresponding
        keys. Note that the keys in the JSON file must be exactly the same as the names
        of the class fields.

        This method through inheritance will be used to construct task-specific configs

        :param json_path: path to JSON config file (str or pathlib.Path)
        :param sub_jsons: if True, check every value in config JSON to be a path to a lower level JSON config (bool)
        :return: class with values from JSON config assigned to the class fields
        """

        if type(json_path) == str:
            json_path = Path(json_path)

        config_dict = data_utils.load_json_from_disk(json_path, sub_jsons=sub_jsons)
        return cls.config_from_dict(config_dict, auth_config)

    @classmethod
    def config_from_dict(
        cls, config_dict: dict, auth_config: TrojAuthConfig = None
    ) -> "BaseTrojARtConfig":
        """Given a dictionary, initializes fields with values from corresponding keys"""

        invalid_paths = data_utils.test_paths(config_dict)

        if len(invalid_paths) > 0:
            err = TrojConfigError(
                "\n\nSome paths provided were invalid!"
                + "\n"
                + "Please ensure the following paths are correct:"
                + "\n"
                + str(invalid_paths)
                + "\n\n"
                + "The current working directory is:"
                + "\n"
                + str(os.getcwd())
                + "\n\n"
                + "The following files are in the working directory:"
                + "\n"
                + str(os.listdir())
            )
            raise (err)

        try:
            if auth_config is None:
                auth_config = TrojAuthConfig.config_from_dict(
                    config_dict["auth_config"]
                )
            config_dict["auth_config"] = auth_config

            return cls.from_dict(config_dict)

        except KeyError as err:
            raise TrojConfigError(
                f'\n\nKey "{err.args[0]}" missing from json.'
                "Make sure all required key-value pairs are "
                "present in the json"
            )

        except AttributeError as e:
            log.error(e)
            raise TrojConfigError(
                "\n\nCould not unpack one of sub-jsons. Make sure "
                "that paths to sub-jsons are specified correctly."
            )

        except UndefinedParameterError as err:
            message = str(err)
            dict_substring = (
                "{" + re.findall("{(.+?)}", re.sub("\(.+?\)", "", message))[0] + "}"
            )
            unknown_dict = ast.literal_eval(dict_substring)
            raise TrojConfigError(
                f'\n\nGot unexpected key(s) in json: "{list(unknown_dict)}"\n'
            )

        except TypeError as err:
            raise TrojConfigError(
                f"\n\nInvalid auth_keys datatype; ensure auth_keys is a valid subjson"
            )

        except Exception as err:
            if hasattr(err, "message"):
                raise TrojConfigError(err.message)
            else:
                raise TrojConfigError(repr(err))


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class BaseTrojDataset(DataClassJsonMixin, JsonSchemaMixin):

    """Base dataset class to be extended by dataset classes in the task-specific submodules."""

    name: str
    path_to_data: str
