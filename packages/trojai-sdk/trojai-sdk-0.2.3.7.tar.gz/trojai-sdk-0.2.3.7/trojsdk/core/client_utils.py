import json
import numpy as np
from typing import Tuple
from pathlib import Path

from trojsdk.client import TrojClient
from trojsdk.config.auth import TrojAuthConfig
from trojsdk.config.base import BaseTrojConfig, BaseTrojARtConfig
from trojsdk.config.cybersecval_config import BaseTrojCyberSecConfig
from trojsdk.config.nlp import NLPTrojConfig
from trojsdk.config.tabular import TabularTrojConfig
from trojsdk.config.vision import VisionTrojConfig
from trojsdk.core import data_utils, troj_logging

log = troj_logging.getLogger(__file__)

"""
The troj job handler class wraps the client and stores all details relevant to a given job or session.
"""


def submit_evaluation(
    path_to_config: str = None,
    config: dict = None,
    docker_metadata=None,
    k8s_metadata=None,
    nossl=False,
) -> "TrojJobHandler":
    """
    Submit a job using the specified config.
    Either path_to_config or config are required, path_to_config takes priority.

    :param path_to_config: The path of a JSON file containing your config for the evaluation.
    :param config: A dict containing your config for the evaluation.
    :param docker_metadata: A dict containing two entries; "docker-image" and "docker_secret_name". Default values are trojai/troj-engine-base-<type>:<tabluar>-predev-latest and trojaicreds respectively.
    """

    if path_to_config is not None:
        config = data_utils.load_json_from_disk(Path(path_to_config))
        log.info("JSON loaded from disk.")

    config, docker_metadata, k8s_metadata = config_from_dict(config, docker_metadata)
    tjh = TrojJobHandler()
    response = tjh.post_job_to_endpoint(config, docker_metadata, k8s_metadata, nossl)
    log.info("Config posted to endpoint")
    log.info("Response: " + str(response))

    return tjh


def submit_autoredteaming(
    path_to_config: str = None,
    config: dict = None,
    docker_metadata=None,
    k8s_metadata=None,
    nossl=False,
) -> "TrojJobHandler":
    """
    Submit a job using the specified config.
    Either path_to_config or config are required, path_to_config takes priority.

    :param path_to_config: The path of a JSON file containing your config for the evaluation.
    :param config: A dict containing your config for the evaluation.
    :param docker_metadata: A dict containing two entries; "docker-image" and "docker_secret_name". Default values are trojai/troj-engine-base-<type>:<tabluar>-predev-latest and trojaicreds respectively.
    """
    if path_to_config is not None:
        config = data_utils.load_json_from_disk(Path(path_to_config))
        log.info("JSON loaded from disk.")

    config, docker_metadata, k8s_metadata = art_config_from_dict(
        config, docker_metadata, k8s_metadata
    )

    tjh = TrojJobHandler()

    response = tjh.post_art_job_to_endpoint(
        config, docker_metadata, k8s_metadata, nossl
    )

    log.info("Auto-Redteaming config posted to endpoint")
    log.info("Response: " + str(response))

    return tjh


def submit_cybersec(
    path_to_config: str = None,
    config: dict = None,
    docker_metadata=None,
    k8s_metadata=None,
    nossl=False,
) -> "TrojJobHandler":
    """
    Submit a job using the specified config.
    Either path_to_config or config are required, path_to_config takes priority.

    :param path_to_config: The path of a JSON file containing your config for the CyberSec.
    :param config: A dict containing your config for the CyberSec.
    :param docker_metadata: A dict containing two entries; "docker-image" and "docker_secret_name".
    """
    if path_to_config is not None:
        config = data_utils.load_json_from_disk(Path(path_to_config))
        log.info("JSON loaded from disk.")

    config, docker_metadata, k8s_metadata = cybersec_config_from_dict(
        config, docker_metadata, k8s_metadata
    )

    tjh = TrojJobHandler()

    response = tjh.post_cybersec_job_to_endpoint(
        config, docker_metadata, k8s_metadata, nossl
    )

    log.info("CyberSec config posted to endpoint")
    log.info("Response: " + str(response))

    return tjh


def submit_evaluation_TEST(
    path_to_config: str = None,
    config: dict = None,
    docker_metadata=None,
    k8s_metadata=None,
    nossl=False,
) -> "TrojJobHandler":
    """
    TESTING USE ONLY
    FAKE version of submit_evaluation
    Exists to mimic a valid post call + response from submit_evaluation without filling up environments with extra pods
    Either path_to_config or config are required, path_to_config takes priority.

    :param path_to_config: The path of a JSON file containing your config for the evaluation.
    :param config: A dict containing your config for the evaluation.
    :param docker_metadata: A dict containing two entries; "docker-image" and "docker_secret_name". Default values are trojai/troj-engine-base-<type>:<tabluar>-predev-latest and trojaicreds respectively.
    """

    if path_to_config is not None:
        config = data_utils.load_json_from_disk(Path(path_to_config))
        log.info("JSON loaded from disk.")

    config, docker_metadata, k8s_metadata = config_from_dict(config, docker_metadata)
    tjh = TrojJobHandler()
    # replace actual job posting with copy of all non-api-linked
    # functionality of post_job_to_endpoint()
    # and sets a fake 200 response dict
    tjh.client = TrojClient(auth_config=config.auth_config, nossl=nossl)
    tjh.post_response = {
        "status_code": 200,
        "data": {
            "job_id": "task made",
            "job_name": "trojeval-tabular-DUMMY-RESPONSE",
            "test_run_uuid": "DUMMY-UUID",
        },
    }

    log.info("Config NOT posted to endpoint - this is the testing function")

    return tjh


def config_from_dict(
    config: dict, docker_metadata: dict = None, k8s_metadata: dict = None
) -> Tuple[BaseTrojConfig, dict]:
    """
    :param config: The config file to be converted to a BaseTrojConfig type; NLPTrojConfig, TabularTrojConfig, or VisionTrojConfig. Determined by "task_type" within the config.
    :type config: dict
    :param docker_metadata: The dict containing the current docker data, if any. If supplied, this field will be prioritized over the docker_metadata in the config. Defaults to None.
    :type docker_metadata: dict, optional

    :return: The BaseTrojConfig type object, with "docker_metadata" popped off, if it existed. Tuples with docker_metadata with the following descending priority: parameter from this func, field from config, default value for given task_type.
    :rtype: Tuple[BaseTrojConfig, dict]
    """

    config_km = None
    if config.get("k8s_metadata"):
        config_km = config.pop("k8s_metadata")

    if not k8s_metadata:
        if config_km:
            k8s_metadata = config_km

    config_dm = None
    if config.get("docker_metadata"):
        config_dm = config.pop("docker_metadata")

    if not docker_metadata:
        if config_dm:
            docker_metadata = config_dm
        else:
            docker_metadata = get_default_docker_metadata(config.get("task_type"))

    if not docker_metadata.get("image_pull_policy"):
        docker_metadata["image_pull_policy"] = "Always"
    if docker_metadata.get("docker_secret_name") is None:
        docker_metadata["docker_secret_name"] = "None"
    try:
        if config["task_type"] == "nlp":
            config = NLPTrojConfig.config_from_dict(config)
        elif config["task_type"] == "tabular":
            config = TabularTrojConfig.config_from_dict(config)
        elif config["task_type"] == "vision":
            config = VisionTrojConfig.config_from_dict(config)
        else:
            raise Exception(
                f"Model type {config['task_type']} not found. Please select one of [tabular, nlp, vision]."
            )
    except Exception as e:
        raise Exception(f"Missing task_type: " + str(e))

    return config, docker_metadata, k8s_metadata


def art_config_from_dict(
    config: dict, docker_metadata: dict = None, k8s_metadata: dict = None
) -> Tuple[BaseTrojARtConfig, dict, dict]:
    """
    :param config: The config file to be converted to a BaseTrojConfig type; NLPTrojConfig, TabularTrojConfig, or VisionTrojConfig. Determined by "task_type" within the config.
    :type config: dict
    :param docker_metadata: The dict containing the current docker data, if any. If supplied, this field will be prioritized over the docker_metadata in the config. Defaults to None.
    :type docker_metadata: dict, optional

    :return: The BaseTrojConfig type object, with "docker_metadata" popped off, if it existed. Tuples with docker_metadata with the following descending priority: parameter from this func, field from config, default value for given task_type.
    :rtype: Tuple[BaseTrojConfig, dict]
    """

    config_km = None
    if config.get("k8s_metadata"):
        config_km = config.get("k8s_metadata", {})

    if not k8s_metadata:
        if config_km:
            k8s_metadata = config_km

    config_dm = None
    if config.get("docker_metadata"):
        config_dm = config.get("docker_metadata", {})

    if not docker_metadata:
        if config_dm:
            docker_metadata = config_dm
        else:
            docker_metadata = get_default_docker_metadata(config.get("task_type"))

    if not docker_metadata.get("image_pull_policy"):
        docker_metadata["image_pull_policy"] = "Always"
    if docker_metadata.get("docker_secret_name") is None:
        docker_metadata["docker_secret_name"] = "None"

    config = BaseTrojARtConfig.config_from_dict(config)

    return config, docker_metadata, k8s_metadata


def cybersec_config_from_dict(
    config: dict, docker_metadata: dict = None, k8s_metadata: dict = None
) -> Tuple[BaseTrojCyberSecConfig, dict, dict]:
    """
    :param config: The config file to be converted to a BaseTrojCyberSecConfig.
    :type config: dict
    :param docker_metadata: The dict containing the current docker data, if any. If supplied, this field will be prioritized over the docker_metadata in the config. Defaults to None.
    :type docker_metadata: dict, optional

    :return: The BaseTrojCyberSecConfig type object, with "docker_metadata" popped off, if it existed. Tuples with docker_metadata with the following descending priority: parameter from this func, field from config, default value for given task_type.
    :rtype: Tuple[BaseTrojCyberSecConfig, dict]
    """

    config_k8s_meta = None
    if config.get("k8s_metadata"):
        config_k8s_meta = config.get("k8s_metadata", {})

    if not k8s_metadata:
        if config_k8s_meta:
            k8s_metadata = config_k8s_meta

    config_docker_meta = None
    if config.get("docker_metadata"):
        config_docker_meta = config.get("docker_metadata", {})

    if not docker_metadata:
        if config_docker_meta:
            docker_metadata = config_docker_meta
        else:
            docker_metadata = get_default_docker_metadata(config.get("task_type"))

    if not docker_metadata.get("image_pull_policy"):
        docker_metadata["image_pull_policy"] = "Always"
    if docker_metadata.get("docker_secret_name") is None:
        docker_metadata["docker_secret_name"] = "None"

    config = BaseTrojCyberSecConfig.config_from_dict(config)

    return config, docker_metadata, k8s_metadata


def get_default_docker_metadata(task_type: str):
    docker_metadata = {
        "docker_secret_name": "trojaicreds",
        "image_pull_policy": "Always",
    }
    try:
        docker_choices_dict = {
            "tabular": "trojai/troj-engine-base-tabular:tabluar-dev-latest",
            "nlp": "trojai/troj-engine-base-nlp:nlp-dev-latest",
            "vision": "trojai/troj-engine-base-cv:cv-dev-latest",
        }
        docker_metadata["docker_image_url"] = docker_choices_dict[
            str(task_type).lower()
        ]
    except Exception as e:
        raise Exception(
            f"Model type {task_type} not found. Please select one of "
            + str(list(docker_choices_dict))
        ) from e

    return docker_metadata


class TrojJobHandler:
    def __init__(self) -> None:
        self.client = None
        self.post_response = None
        self.status_response = None

    def post_job_to_endpoint(
        self,
        config: BaseTrojConfig,
        docker_metadata: dict = None,
        k8s_metadata: dict = None,
        nossl=False,
    ) -> dict:
        """
        This function posts any given config to the endpoint.

        :param config: The main configuration for the project.
        :type config: BaseTrojConfig
        :param docker_metadata: A dictionary with the following two values;
            "docker_image_url": A Docker Hub image id for any engine type.
                Ex. value: "trojai/troj-engine-base-tabular:tabluar-shawn-latest"
            "docker_secret_name": The name of the environment secret containing the credentials for Docker Hub access. This is defined in the TrojAI helm repo in the _setup.sh_ script.
        :type docker_metadata: dict, optional

        :return: Contains job_name under key "data", under key "job_name". (Dict within dict)
        :rtype: dict
        """

        self.client = TrojClient(auth_config=config.auth_config, nossl=nossl)
        res = self.client.post_job(config, docker_metadata, k8s_metadata, nossl)
        self.post_response = res
        return res

    def post_art_job_to_endpoint(
        self,
        config: BaseTrojARtConfig,
        docker_metadata: dict = None,
        k8s_metadata: dict = None,
        nossl=False,
    ) -> dict:
        """
        This function posts any given config to the endpoint.

        :param config: The main configuration for the project.
        :type config: BaseTrojConfig
        :param docker_metadata: A dictionary with the following two values;
            "docker_image_url": A Docker Hub image id for any engine type.
                Ex. value: "trojai/troj-engine-base-tabular:tabluar-shawn-latest"
            "docker_secret_name": The name of the environment secret containing the credentials for Docker Hub access. This is defined in the TrojAI helm repo in the _setup.sh_ script.
        :type docker_metadata: dict, optional

        :return: Contains job_name under key "data", under key "job_name". (Dict within dict)
        :rtype: dict
        """
        self.client = TrojClient(auth_config=config.auth_config, nossl=nossl)
        res = self.client.post_autoredteaming_job(
            config, docker_metadata, k8s_metadata, nossl
        )
        self.post_response = res
        return res

    def post_cybersec_job_to_endpoint(
        self,
        config: BaseTrojCyberSecConfig,
        docker_metadata: dict = None,
        k8s_metadata: dict = None,
        nossl=False,
    ) -> dict:
        """
        This function posts any given config to the endpoint.

        :param config: The main configuration for the project.
        :type config: BaseTrojConfig
        :param docker_metadata: A dictionary with the following two values;
            "docker_image_url": A Docker Hub image id for any engine type.
                Ex. value: "trojai/troj-engine-base-tabular:tabluar-shawn-latest"
            "docker_secret_name": The name of the environment secret containing the credentials for Docker Hub access. This is defined in the TrojAI helm repo in the _setup.sh_ script.
        :type docker_metadata: dict, optional

        :return: Contains job_name under key "data", under key "job_name". (Dict within dict)
        :rtype: dict
        """
        self.client = TrojClient(auth_config=config.auth_config, nossl=nossl)
        res = self.client.post_cybersec_job_to_endpoint(
            config, docker_metadata, k8s_metadata, nossl
        )
        self.post_response = res
        return res

    def create_client(self, troj_experimenter, nossl=False):
        self.client = TrojClient(api_endpoint=troj_experimenter.api_endpoint)
        self.client._creds_api_key = troj_experimenter.auth_keys["api_key"]
        self.client._secrets = troj_experimenter.secrets
        self.client.nossl = True

    def list_stress_test_jobs(
        self,
        project_name=None,
        dataset_name=None,
        test_run_name=None,
        status="ALL",
        wait=False,
        polling_rate=2,
        pretty=True,
    ):
        """
        Ping backend route for all jobs.
        :param project_name: optional, returns only jobs under given project
        :param status: optional, you can get jobs with any specified kubernetes pod status
        :param wait: optional, waits on pods until they all return completed or equivalent ended status
        :param polling_rate: default 2s, polling rate
        :param pretty: cuts down on some of the pod output to make it easier to view in terminal
        :return: if wait/blocking not desired, the function will return a call to the client's job list function
        :rtype: function

        """
        import time

        # get initial job list
        jobs = self.client.list_stress_test_jobs(
            project_name=project_name,
            dataset_name=dataset_name,
            test_run_name=test_run_name,
            status=status,
        )
        stat_res = []
        # create headers for output
        print_out = (
            "{:<40} {:<20} {:<48} {:<35} {:<20}".format(
                "job_name",
                "| state",
                "| test_run_name",
                "| creation_timestamp",
                "| start_time",
            )
            + "\n"
        )
        # parse job data into output
        for job in jobs:
            if pretty:
                print_out += "{:<40} {:<20} {:<48} {:<35} {:<20}".format(
                    str(job.get("job_name")),
                    "| " + str(job.get("state")),
                    "| " + str(job.get("test_run_name")),
                    "| " + str(job.get("creation_timestamp")),
                    "| " + str(job.get("start_time")),
                )
                print_out += "\n"
        # print full output on first run
        if pretty:
            print(print_out)
        else:
            print(str(jobs))
        # loop through pings until all are completed
        if wait:
            print("Watching for all jobs to be finished...")
            # SETS VERSION
            # this turns the jobs into Tuples so that they can be used in a Set
            watched_statuses = [
                (
                    job.get("job_name"),
                    job.get("state"),
                    job.get("test_run_name"),
                    job.get("creation_timestamp"),
                    job.get("start_time"),
                )
                for job in jobs
            ]
            old = set(watched_statuses)
        while wait:
            # SETS VERSION
            # check whether statuses are completed
            stat_res = [
                job.get("state") in TrojJobStatuses.dead_statuses for job in jobs
            ]
            # transform jobs to Set of Tuples (dict cannot be hashed to set)
            jobSet = set(
                [
                    (
                        job.get("job_name"),
                        job.get("state"),
                        job.get("test_run_name"),
                        job.get("creation_timestamp"),
                        job.get("start_time"),
                    )
                    for job in jobs
                ]
            )
            # compare current job set to previous iteration
            for job in jobSet - old:
                print_out = "{:<40} {:<20} {:<48} {:<35} {:<20}".format(
                    str(job[0]),  # job name
                    "| " + str(job[1]),  # state
                    "| " + str(job[2]),  # test run name
                    "| " + str(job[3]),  # creation timestamp
                    "| " + str(job[4]),  # start time
                )
                print(print_out)
            old = jobSet

            # check if loop can end
            if all(stat_res):
                wait = False
                print("No jobs running!")
            # if not everything is done, wait polling_rate seconds and ping api again
            else:
                time.sleep(polling_rate)
                jobs = self.client.list_stress_test_jobs(
                    project_name=project_name,
                    dataset_name=dataset_name,
                    test_run_name=test_run_name,
                    status=status,
                )

        return jobs

    def extract_run(self, job_name):
        """
        this function returns everything needed for the df extraction run as well as the full download
        should I make a class to hold all the values or what
        """
        stop = False
        while not stop:
            run_json = self.client.download_test_run(job_name)
            if run_json is None:
                import time

                time.sleep(5)
                continue
            stop = True
            r = json.loads(run_json)
            t_o = TrojOutput(r)
        self.engine_results = t_o
        return t_o


class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyArrayEncoder, self).default(obj)


class TrojJobStatuses:
    """
    This class holds some kubernetes statuses for easy access
    """

    UNKNOWN = "Unknown"
    CREATING = "ContainerCreating"
    PENDING = "Pending"
    RUNNING = "Running"
    FAILED = "Failed"
    ERROR = "Error"
    COMPLETED = "Completed"
    DNE = "DNE"
    dead_statuses = [UNKNOWN, FAILED, COMPLETED, ERROR, DNE]
    alive_statuses = [PENDING, RUNNING, CREATING]


class TrojOutput:
    """
    This class stores the output of a test run, all the dataframe types are accessible as dataframes
    """

    def __init__(self, dict):
        import pandas

        self.full_output = dict
        pandas_dict = {}
        df = dict.get("dataframe")
        for key in df.keys():
            pandas_dict[key] = pandas.DataFrame(df.get(key))
        self.dataframe = pandas_dict
        self.config = dict.get("config")
        self.metrics = dict.get("metrics")
        self.integrity = dict.get("integrity")
        self.graphs = dict.get("graphs")
        self.metadata = dict.get("metadata")
        self.key_insights = dict.get("key_insights")

    def return_failed_samples(self):
        # build dict of failed samples
        no_base_dict = self.full_output.get("dataframe")
        no_base_dict.pop("base")
        output_dict = {}
        # filter self.dataframe not including base
        for attack in no_base_dict:
            # filter for failed attacks
            output_dict[attack] = []
            for sample in no_base_dict.get(attack):
                if sample.get("model_success") == "failed":
                    output_dict[attack].append(sample)

        return output_dict

    def wandb_upload(self):
        try:
            import wandb
            import plotly

            wandb.init(
                # set the wandb project where this run will be logged
                # get proj names from config
                project="test_run_name",
            )
            for key in self.dataframe.keys():
                tbl = wandb.Table(dataframe=self.dataframe[key])
                wandb.log({key: tbl})
            for key in self.graphs:
                graph = wandb.Plotly(plotly.io.from_json(json.dumps(self.graphs[key])))
                wandb.log({key: graph})

            wandb.run.summary["key_insights"] = self.key_insights
            wandb.run.summary["integrity"] = self.integrity
            wandb.run.summary["metadata"] = self.metadata
            wandb.run.summary["metrics"] = self.metrics
            wandb.run.summary["config"] = self.config
            wandb.finish()
            return True
        except Exception as e:
            print(e)
            print("something went wrong with the wandb upload")
            return False
