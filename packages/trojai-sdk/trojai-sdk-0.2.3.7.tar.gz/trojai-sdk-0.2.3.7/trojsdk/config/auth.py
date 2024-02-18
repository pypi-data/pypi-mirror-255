import os
import re
import ast
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Union
from dataclasses import dataclass
from dataclasses_jsonschema import JsonSchemaMixin
from dataclasses_json.undefined import UndefinedParameterError
from dataclasses_json import dataclass_json, DataClassJsonMixin, Undefined
from trojsdk.core.troj_error import TrojConfigError
from trojsdk.core import data_utils, troj_logging

log = troj_logging.getLogger(__file__)


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class AuthKeys(DataClassJsonMixin, JsonSchemaMixin):
    """Dataclass to store keys for SAAS auth"""

    api_key: str


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class TrojAuthConfig(DataClassJsonMixin, JsonSchemaMixin):
    """Dataclass to hold Authentication details and posting details"""

    api_endpoint: str
    auth_keys: AuthKeys
    project_name: Optional[str]
    dataset_name: Optional[str] = None
    job_name: Optional[str] = None
    secrets: Optional[dict] = None

    @classmethod
    def _checkGAC(cls, config: "TrojAuthConfig") -> "TrojAuthConfig":
        try:
            config.secrets["GOOGLE_APPLICATION_CREDENTIALS"] = json.dumps(
                config.secrets.get("GOOGLE_APPLICATION_CREDENTIALS")
            )
        except:
            pass
        return config

    @classmethod
    def config_from_json(
        cls, json_path: Union[str, Path], sub_jsons: bool = True
    ) -> "TrojAuthConfig":
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
        return cls.config_from_dict(config_dict)

    @classmethod
    def config_from_dict(cls, config_dict: dict) -> "TrojAuthConfig":
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
            raise err

        try:
            config = cls.from_dict(config_dict)
            config = cls._checkGAC(config)

            config.api_endpoint = re.sub(
                r"/+$", r"", config.api_endpoint
            )  # Remove any "/" characters at the end

            return config

        except KeyError as err:
            raise TrojConfigError(
                f'\n\nKey "{err.args[0]}" missing from json.'
                "Make sure all required key-value pairs are "
                "present in the json"
            )

        except UndefinedParameterError as err:
            message = str(err)
            dict_substring = (
                "{" + re.findall("{(.+?)}", re.sub("\(.+?\)", "", message))[0] + "}"
            )
            unknown_dict = ast.literal_eval(dict_substring)
            raise TrojConfigError(
                f'\n\nGot unexpected key(s) in json: "{list(unknown_dict.keys())}"\n'
            )
        except Exception as err:
            if hasattr(err, "message"):
                raise TrojConfigError(err.message)
            else:
                raise TrojConfigError(repr(err))
