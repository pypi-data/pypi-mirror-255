import requests
from typing import Optional, List
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests import Session
from urllib import parse
import re

from trojsdk.config.auth import TrojAuthConfig
from trojsdk.config.base import BaseTrojConfig, BaseTrojARtConfig
from trojsdk.config.cybersecval_config import BaseTrojCyberSecConfig

retry_strategy = Retry(
    total=2,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "PUT", "POST", "DELETE", "OPTIONS", "TRACE"],
)

retry_adapter = HTTPAdapter(max_retries=retry_strategy)
requests_retry = Session()
requests_retry.mount("https://", retry_adapter)
requests_retry.mount("http://", retry_adapter)

"""
Troj Client class handls all requests made to a passed endpoint
"""


class TrojClient:
    api_endpoint: str = None
    refresh_url: str = None
    nossl: bool = False

    _auth_config: TrojAuthConfig = None

    _creds_api_key: str = None
    _secrets: dict = None

    def __init__(
        self,
        *,
        api_endpoint: str = "http://localhost:8080/api/v1",
        auth_config: TrojAuthConfig = None,
        nossl=False,
        **kwargs,
    ):
        if auth_config is not None:
            self.api_endpoint = auth_config.api_endpoint
            self._auth_config = auth_config
            self._creds_api_key = auth_config.auth_keys.api_key
            self._secrets = auth_config.secrets

        else:
            self.api_endpoint = api_endpoint
        self.nossl = nossl

        # requests_retry.hooks["response"].append(
        #     self.reauth
        # )  # https://github.com/psf/requests/issues/4747 - Important for Retry vs urllib3

    def _get_creds_headers(self):
        """
        Get appropriate request headers for the currently set credentials.

        Raises:
            Exception: No credentials set.
        """
        if self._creds_api_key:
            return {
                # "Authorization": f"Bearer {self._creds_id_token}",
                "x-troj-api-key": f"{self._creds_api_key}"
            }
        else:
            raise Exception("No credentials set.")

    def set_credentials(
        self,
        *,
        api_key: Optional[str] = None,
        auth_config: Optional[TrojAuthConfig] = None,
    ):
        """
        Set credentials for the client.

        :param api_key (str, optional): Used to gain access to API.

        Raises:
            Exception: Invalid credential combination provided.
        """

        if api_key is not None:
            self._creds_api_key = api_key

        if auth_config is not None:
            self._auth_config = auth_config

    def get_jobs(self):
        r = requests_retry.get(
            f"{self.api_endpoint}/sdk/jobs",
            headers=self._get_creds_headers(),
            verify=not self.nossl,
        )
        return r

    def post_job(
        self,
        config: BaseTrojConfig,
        docker_metadata: dict = None,
        k8s_metadata: dict = None,
        use_auth_from_config: bool = False,
        # nossl: bool = False
    ) -> dict:
        """
        When using different sources of authentication and api endpoints, keep in mind that the client's auth_config will remain the unchanged.
        Use client.set_credentials() to change auth_config context.

        :param config: Uses BaseTrojConfig (NLPTrojConfig, TabularTrojConfig, or VisionTrojConfig)
            The main configuration for the project.
        :type config: BaseTrojConfig

        :param docker_metadata: A dictionary with the following two values;
            "docker_image_url": A Docker Hub image id for any engine type.
                Ex. value: "trojai/troj-engine-base-tabular:tabluar-shawn-latest"
            "docker_secret_name": The name of the environment secret containing the credentials for Docker Hub access. This is defined in the TrojAI helm repo in the _setup.sh_ script.
            Leaving none will default to the latest image.
        :type docker_metadata: dict, optional

        :param use_auth_config_from_config: Use the api keys and api endpoint from the config's authentication values, not from the client object.
        :type use_auth_from_config: bool, optional

        :return: Contains job_name under key "data", under key "job_name". (Dict within dict)
        :rtype: dict
        """

        # Keep the project name and dataset name from the config, but set auth keys from client's TrojAuthConfig
        if not use_auth_from_config:
            proj_name = config.auth_config.project_name
            dset_name = config.auth_config.dataset_name

            config.auth_config = self._auth_config

            config.auth_config.project_name = proj_name
            config.auth_config.dataset_name = dset_name

        data = {
            "job_config": {"body": config.to_dict()},
            "docker_metadata": docker_metadata,
            "k8s_metadata": k8s_metadata,
        }

        r = requests_retry.post(
            f"{config.auth_config.api_endpoint}/sdk/jobs",
            headers=self._get_creds_headers(),
            json=data,
            verify=not self.nossl,
        )

        self.raise_resp_exception_error(r)

        return {"status_code": r.status_code, "data": r.json()}

    def post_autoredteaming_job(
        self,
        config: BaseTrojARtConfig,
        docker_metadata: dict = None,
        k8s_metadata: dict = None,
        use_auth_from_config: bool = False,
        nossl: bool = False,
    ) -> dict:
        """
        When using different sources of authentication and api endpoints, keep in mind that the client's auth_config will remain the unchanged.
        Use client.set_credentials() to change auth_config context.

        :param config: Uses BaseTrojConfig (NLPTrojConfig, TabularTrojConfig, or VisionTrojConfig)
            The main configuration for the project.
        :type config: BaseTrojConfig

        :param docker_metadata: A dictionary with the following two values;
            "docker_image_url": A Docker Hub image id for any engine type.
                Ex. value: "trojai/troj-engine-base-tabular:tabluar-shawn-latest"
            "docker_secret_name": The name of the environment secret containing the credentials for Docker Hub access. This is defined in the TrojAI helm repo in the _setup.sh_ script.
            Leaving none will default to the latest image.
        :type docker_metadata: dict, optional

        :param use_auth_config_from_config: Use the api keys and api endpoint from the config's authentication values, not from the client object.
        :type use_auth_from_config: bool, optional

        :return: Contains job_name under key "data", under key "job_name". (Dict within dict)
        :rtype: dict
        """

        # Keep the project name and dataset name from the config, but set auth keys from client's TrojAuthConfig
        # if not use_auth_from_config:
        #     proj_name = config.auth_config.project_name
        #     dset_name = config.auth_config.dataset_name

        #     config.auth_config = self._auth_config

        #     config.auth_config.project_name = proj_name
        #     config.auth_config.dataset_name = dset_name

        data = config.to_dict()

        r = requests_retry.post(
            f"{self.api_endpoint}/sdk/submit-art-job-config",
            headers=self._get_creds_headers(),
            json=data,
            verify=not self.nossl,
        )

        self.raise_resp_exception_error(r)

        return {"status_code": r.status_code, "data": r.json()}

    def post_cybersec_job_to_endpoint(
        self,
        config: BaseTrojCyberSecConfig,
        docker_metadata: dict = None,
        k8s_metadata: dict = None,
        use_auth_from_config: bool = False,
        nossl: bool = False,
    ) -> dict:
        """
        When using different sources of authentication and api endpoints, keep in mind that the client's auth_config will remain the unchanged.
        Use client.set_credentials() to change auth_config context.

        :param config: Uses BaseTrojCyberSecConfig
            The main configuration for the project.
        :type config: BaseTrojConfig

        :param docker_metadata: A dictionary with the following two values;
            "docker_image_url": A Docker Hub image id for any engine type.
                Ex. value: "trojai/troj-engine-base-tabular:tabluar-shawn-latest"
            "docker_secret_name": The name of the environment secret containing the credentials for Docker Hub access. This is defined in the TrojAI helm repo in the _setup.sh_ script.
            Leaving none will default to the latest image.
        :type docker_metadata: dict, optional

        :param use_auth_config_from_config: Use the api keys and api endpoint from the config's authentication values, not from the client object.
        :type use_auth_from_config: bool, optional

        :return: Contains job_name under key "data", under key "job_name". (Dict within dict)
        :rtype: dict
        """

        # Keep the project name and dataset name from the config, but set auth keys from client's TrojAuthConfig
        # if not use_auth_from_config:
        #     proj_name = config.auth_config.project_name
        #     dset_name = config.auth_config.dataset_name

        #     config.auth_config = self._auth_config

        #     config.auth_config.project_name = proj_name
        #     config.auth_config.dataset_name = dset_name

        data = {
            "job_config": config.to_dict(),
            "docker_metadata": docker_metadata,
            "k8s_metadata": k8s_metadata,
        }

        r = requests_retry.post(
            f"{self.api_endpoint}/sdk/submit-cybersec-job-config",
            headers=self._get_creds_headers(),
            json=data,
            verify=not self.nossl,
        )

        self.raise_resp_exception_error(r)

        return {"status_code": r.status_code, "data": r.json()}

    def raise_resp_exception_error(self, resp):
        if not resp.ok:
            message = None
            try:
                r_body = resp.json()
                message = r_body.get("message") or r_body.get("msg")
            except:
                # If we failed for whatever reason (parsing body, etc.)
                # Just return the code
                if resp.status_code == 500:
                    raise Exception(
                        f"HTTP Error received: {resp.reason}: {str(resp.status_code)}"
                    )
                else:
                    raise Exception(
                        f"HTTP Error received: {resp.reason}: {str(resp.status_code)}"
                    )
            if message:
                raise Exception(f"Error: {message}")
            else:
                if resp.status_code == 500:
                    raise Exception(
                        f"HTTP Error received: {resp.reason}: {str(resp.status_code)}"
                    )
                else:
                    raise Exception(
                        f"HTTP Error received: {resp.reason}: {str(resp.status_code)} | {resp.json()['detail']}"
                    )

    def list_stress_test_jobs(
        self, project_name=None, dataset_name=None, test_run_name=None, status="ALL"
    ):
        """
        Takes in optional proj/dataset/test run, pings backend job table for all jobs then filters results. Specific statuses can be sent also
        """
        # get & decode list of all jobs
        r = requests_retry.get(
            f"{self.api_endpoint}/sdk/jobs/",
            headers=self._get_creds_headers(),
            verify=not self.nossl,
        )
        decoded_response = json.loads(r.content)
        # filter job list based on state, project_name, and test_run_name if filters are defined
        if status != "ALL":
            decoded_response = self.filter_jobs("state", status, decoded_response)
        if project_name != None:
            decoded_response = self.filter_jobs(
                "project_name", project_name, decoded_response
            )
        if test_run_name != None:
            decoded_response = self.filter_jobs(
                "test_run_name", test_run_name, decoded_response
            )
        return decoded_response

    def filter_jobs(self, field, value, decoded_response):
        # filter jobs based on field (ex: status) having specified value (ex: completed)
        filtered_response = []
        for pod in decoded_response:
            if value in pod.get(field):
                filtered_response.append(pod)
        return filtered_response

    def download_test_run(self, job_name):
        """
        First gets all the uuids of a given test run name, then uses those to pull the run output back to the sdk
        """
        r = requests_retry.get(
            f"{self.api_endpoint}/sdk/job/{job_name}",
            headers=self._get_creds_headers(),
            verify=not self.nossl,
        )
        decoded_response = json.loads(r.content)
        podState = decoded_response.get("ContainerStatus").get("state")
        proj = decoded_response.get("project_uuid")
        dset = decoded_response.get("TestRun").get("dataset_uuid")
        test = decoded_response.get("TestRun").get("test_run_uuid")
        if proj is None or dset is None or test is None or podState == "Error":
            raise (
                Exception("Kubernetes pod errored! Check the logs for the errored pod.")
            )
        r2 = requests_retry.get(
            f"{self.api_endpoint}/sdk/projects/{proj}/datasets/{dset}/test-runs/{test}/download-output",
            headers=self._get_creds_headers(),
            verify=not self.nossl,
        )

        return json.loads(r2.content)

    def generate_api_key(self, description, expiry):
        """
        Uses provided description and expiry to ping backend and request api key (using current key for validation)
        """
        # check that fields have been provided
        if description is None or len(description) < 1:
            raise Exception("Description is required to create a new key!")
        if expiry is None or len(expiry) < 1:
            raise Exception("Expiry is required to create a new key!")
        # ensure expiry is valid format
        pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$"
        match = re.search(pattern, expiry)
        if match is None:
            raise Exception("Invalid expiry provided: " + expiry)
        description = parse.quote_plus(description)  # ensure name is url valid
        expiry = parse.quote_plus(expiry)  # ensure expiry is url valid
        r = requests_retry.post(
            f"{self.api_endpoint}/sdk/api-keys?description={description}&expiry={expiry}",
            headers=self._get_creds_headers(),
            verify=not self.nossl,
        )
        try:
            decoded_response = json.loads(r.content)
        except:
            print("Error: invalid content returned from api.\nContent:", r.content)
            decoded_response = False
        return decoded_response

    def _get_all_api_keys(self):
        """
        Pings api for list of all api keys with their description and expiry
        """
        r = requests_retry.get(
            f"{self.api_endpoint}/sdk/api-keys",
            headers=self._get_creds_headers(),
            verify=not self.nossl,
        )
        decoded_response = json.loads(r.content)
        return decoded_response

    def _chatbot_message(
        self, dynamic_resource, llm_type, config_uuid, client_id, input
    ):
        """
        Pings firewall + model; used only for testing
        All params are MANDATORY
        Data should be object formatted as {"input_string":"message"}
        returns raw Response object
        """
        headers = self._get_creds_headers()
        headers["Dynamic-Resource"] = dynamic_resource
        headers["llm-type"] = llm_type
        headers["config-uuid"] = config_uuid
        headers["client-id"] = client_id

        r = requests_retry.post(
            f"{self.api_endpoint}/sdk/submit", headers=headers, json=input
        )
        return r
