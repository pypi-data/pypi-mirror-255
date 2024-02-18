import os
import json
import warnings
from pathlib import Path
from trojsdk.core.troj_error import TrojJSONError

# Names in this list are keys that will likely store paths to JSON files (e.g. path to JSON of data annotations)
# but following these paths and loading whatever is stored there instead of loading the path itself is undesirable.
JSON_LOADER_EXCLUDED_NAMES = ["path_to_annotations", "save_path"]


def test_paths(input_dict):
    import os

    # from pathlib import Path
    invalid_paths = []
    # loop keys in dict
    for key in input_dict:
        # if value looks like a path
        value = input_dict[key]
        if key == "custom_evaluator_args":
            continue
        if key == "classes_dictionary":
            continue
        if type(value) is dict:
            if key == "auth_keys":
                continue
            dict_data = test_paths(value)
            if dict_data != []:
                for dict_val in dict_data:
                    invalid_paths.append(dict_val)
        elif type(value) is str:
            if value.startswith(("s3://", "gs://", "minio://")):
                continue
            split_str = value.split(".")
            # print(split_str)
            if (
                split_str[-1] == "json"
                or split_str[-1] == "csv"
                or split_str[-1] == "py"
            ):
                if key == "save_path":
                    continue
                # test the path
                path_valid = os.path.exists(value)
                # if invalid, append to invalid paths
                if not path_valid:
                    invalid_paths.append(value)

    return invalid_paths


def load_json_from_disk(json_path: Path, sub_jsons: bool = True) -> dict:
    """
    Given a path to the JSON file in pathlib.Path format, (recursively) read and return the
    dictionary stored in the file.

    Note that when sub_jsons == True and an excluded name is encountered, the contents of the JSON file will not be
    loaded and the path itself will be stored.

    :param json_path: path to the JSON file to load dictionary from (pathlib.Path)
    :param sub_jsons: if True, when path to another existing JSON file is encountered, that JSON file will be loaded
                    recursively instead of saving the path (not applied to names in JSON_LOADER_EXCLUDED_NAMES)(boolean)
    :return: dictionary constructed from the given JSON file (dict)
    """

    try:
        with json_path.open(mode="r") as f:
            json_data = json.load(f)

            if sub_jsons is True:
                for key, value in json_data.copy().items():
                    # iterate over key:value pairs in the source dict
                    if key in JSON_LOADER_EXCLUDED_NAMES:
                        # if key is an excluded name, ignore even if the value is a path to a valid JSON file
                        continue

                    if (
                        type(value) == str
                        and value[-5:] == ".json"
                        and os.path.isfile(value)
                    ):
                        # check that the given value is a string, is a valid path and has a ".json" extension
                        # to separate json paths from actual values
                        json_data[key] = load_json_from_disk(Path(value))

                        # this is needed to support loading attacks from a separate config json
                        if key == "attacks":
                            if (
                                isinstance(json_data[key], dict)
                                and len(json_data[key]) == 1
                                and "attacks" in json_data[key]
                            ):
                                json_data[key] = json_data[key]["attacks"]

                    else:
                        continue
    except Exception as err:
        if hasattr(err, "message"):
            message = err.message
        else:
            message = (
                f"\n\nGot the error: {repr(err)}\n"
                f"Could not load contents of from: {str(json_path)}\n"
                "Make sure that the path to your "
                "JSON file is valid and inside your "
                "JSON is a valid dictionary."
            )

        raise TrojJSONError(message)

    if not json_data:
        warnings.warn(
            "Loaded dictionary from JSON successfully but dictionary is empty.",
            RuntimeWarning,
            stacklevel=2,
        )

    return json_data


from minio import Minio
import os


def minio_upload(
    local_file_path,
    upload_url="minioapi.trojaidev",
    project="proj",
    dataset="dataset",
    model="model",
    minio_user=None,
    minio_pass=None,
    bucket="troj-user-datasets",
):
    if minio_user is None and minio_pass is None:
        raise (
            "No minio credentials supplied for experimenter. Please pass the keys to the experimenter class. Exiting..."
        )
    client = Minio(upload_url, minio_user, minio_pass, secure=False, region=None)
    print(local_file_path)
    if os.path.exists(local_file_path):
        file_name = os.path.basename(local_file_path)
    else:
        raise ("File not found!")

    client.fput_object(
        bucket,
        "/" + project + "/" + dataset + "/" + model + "/" + file_name,
        local_file_path,
    )
    return (
        "minio://"
        + bucket
        + "/"
        + project
        + "/"
        + dataset
        + "/"
        + model
        + "/"
        + file_name
    )
