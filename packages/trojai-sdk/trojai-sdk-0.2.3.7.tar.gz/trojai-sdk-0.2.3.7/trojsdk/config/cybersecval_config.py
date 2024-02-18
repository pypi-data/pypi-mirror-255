"""
Configuration for an CyberSecVal job
"""

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

logger = troj_logging.getLogger(__file__)


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class BaseConfig(DataClassJsonMixin):

    """
    Base class for loading user configs from JSON files
    """

    @classmethod
    def config_from_json(
        cls,
        json_path: Union[str, Path],
        sub_jsons: bool = True,
        auth_config: TrojAuthConfig = None,
    ) -> "BaseConfig":
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
    ) -> "BaseConfig":
        """Given a dictionary, return a dataclass"""

        invalid_file_paths = data_utils.test_paths(config_dict)

        if len(invalid_file_paths) > 0:
            err = TrojConfigError(
                "\n\nSome file paths provided are invalid!"
                + "\n"
                + "Please ensure the following paths are correct:"
                + "\n"
                + str(invalid_file_paths)
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
                f'\n\nKey "{err.args[0]}" missing from json file.'
                "Make sure all required key-value pairs are "
                "present in the json file"
            )

        except AttributeError as e:
            logger.error(e)
            raise TrojConfigError(
                "\n\nCould not unpack one of sub-jsons. Make sure "
                "that file paths to sub-jsons are specified correctly."
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
                f"\n\nInvalid auth_keys datatype; ensure auth_keys is a valid sub-json"
            )

        except Exception as err:
            if hasattr(err, "message"):
                raise TrojConfigError(err.message)
            else:
                raise TrojConfigError(repr(err))

    @classmethod
    def config_from_dict(cls, config_dict: Dict[str, Any]) -> Union["BaseConfig", None]:
        """
        Create instance of class from the given dictionary

        :param config_dict: JSON dictionary
        :return: instance of class
        """

        config_dict.pop("docker_metadata", None)
        config_dict.pop("k8s_metadata", None)

        try:
            return cls.from_dict(config_dict)
        except KeyError as e:
            raise TrojConfigError(f'"{e.args[0]}" key missing from config file')
        except AttributeError as e:
            raise TrojConfigError(f"Malformed config: {e}")
        except UndefinedParameterError as e:
            logger.error(f"{e}")
            raise TrojConfigError(f"{e}")

    def __str__(self):
        """Printable key-value pairs of self"""
        message = "\n  Trojai CyberSecVal configuration:\n"
        num_fields = len(self.__dict__)
        for i, (k, v) in enumerate(self.__dict__.items()):
            message += f"    {k} -- {v}"
            if i < num_fields - 1:
                message += "\n"
        return message


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class BenchmarkConfig(BaseConfig, DataClassJsonMixin):

    """
    Benchmark Config
    """

    benchmark: str
    prompt_path: str
    response_path: str
    stat_path: str
    judge_response_path: Optional[str] = None
    run_llm_in_parallel: Optional[bool] = None


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class BaseTrojCyberSecConfig(BaseConfig, DataClassJsonMixin):

    """CyberSecVal job config"""

    benchmark_config: List[BenchmarkConfig]
    auth_config: Optional[TrojAuthConfig] = None
    save_path: Optional[str] = None
