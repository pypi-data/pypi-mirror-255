import json
from pathlib import Path
import os
import shutil
import pickle
from trojsdk.core.data_utils import minio_upload
import stat


class TrojExperimenter:
    """
    Used for making experiments more reproducible within the troj platform.

    """

    def __init__(self, auth_path):
        """
        Takes in an authentication json which contains the api endpoint and keys for Troj, a bucket name, and a local
        path to save runs to. i.e
        :param auth_path: path to the authentication json.
        """
        with open(auth_path, "r") as fp:
            data = json.load(fp)
        self.api_endpoint = data["api_endpoint"]
        self.auth_keys = data["auth_keys"]
        self.secrets = data["secrets"]
        self.docker_metadata = None
        self.k8s_metadata = None
        self.attacks = None
        self.test_data_conf = None
        self.train_data_conf = None
        if "MINIO_ACCESS_KEY" in self.secrets:
            self.minio_user = self.secrets["MINIO_ACCESS_KEY"]
        else:
            self.minio_user = None
        if "MINIO_SECRET_KEY" in self.secrets:
            self.minio_pass = self.secrets["MINIO_SECRET_KEY"]
        else:
            self.minio_pass = None
        # Default local dev link
        self.minio_url = "minioapi.trojaidev"

    def create_experiment(
        self,
        project_name,
        dataset_name,
        model_name,
        local_save_path="./",
        subtask="classification",
        delete_existing=False,
    ):
        """
        Creates the "experiment" folder locally and on S3

        :param project_name: Name of the project for the troj platform
        :param dataset_name: name of the dataset on the troj platform
        :param model_name: The desired name of the model.
        :param subtask: Subtask type. Default is classification.
        :param delete_existing: If true, will delete previous experiments with the same name. If false, will error
        if names are duplicated.

        :return:
        """

        """
        TODO readd delete existing
        """
        self.local = local_save_path
        self.subtask = subtask
        self.model_name = model_name
        self.custom_evaluator = None
        self.dataset_name = dataset_name
        self.project_name = project_name
        self.experiment_name = "{}/{}/{}/".format(
            project_name, dataset_name, model_name
        )
        self.local_exp_path = os.path.join(self.local, self.experiment_name)
        if delete_existing and os.path.isdir(self.local_exp_path):
            shutil.rmtree(self.local_exp_path)
        os.makedirs(self.local_exp_path, mode=stat.S_IRWXU | stat.S_IRWXG)
        # Path(self.local_exp_path).mkdir(parents=True, exist_ok=True, mode=777)

    def log_data(
        self,
        data_file_path,
        split,
        label_column=None,
        classes_dictionary=None,
        batch_size=16,
        shuffle=False,
        input_column=None,
        target_column=None,
    ):
        """
        Generic function for saving data to the appropriate run file for upload and creating config.

        :param data_file_path: path to data.
        :param label_column: The name of the label column.
        :param split: the split name, used in naming the dataset in the config.
        :param classes_dictionary: Dictionary of class names
        :param batch_size: Desired batch size in config.
        :param shuffle: Whether or not to shuffle the dataframe.
        :return:
        """
        if not data_file_path.startswith(("s3://", "gs://", "minio://")):
            # upload data to minio, local data file
            upload_res = minio_upload(
                data_file_path,
                upload_url=self.minio_url,
                project=self.project_name,
                dataset=self.dataset_name,
                model=self.model_name,
                minio_user=self.minio_user,
                minio_pass=self.minio_pass,
            )
            data_file_path = upload_res
        dloader_config = {"batch_size": batch_size, "shuffle": shuffle}
        if label_column is not None:
            data_config = {
                "name": self.dataset_name + "_" + split,
                "path_to_data": data_file_path,
                "data_loader_config": dloader_config,
                "label_column": label_column,
            }
        elif target_column is not None and input_column is not None:
            data_config = {
                "name": self.dataset_name + "_" + split,
                "path_to_data": data_file_path,
                "data_loader_config": dloader_config,
                "input_column": input_column,
                "target_column": target_column,
            }
        print("No classes dictionary supplied, loading from data config")
        try:
            data_config["classes_dictionary"] = classes_dictionary
        except Exception as e:
            print("No classes dictionary in data config")
            raise (e)

        return data_config

    def log_training_data(
        self,
        path_to_dset_file,
        label_column,
        classes_dictionary=None,
        batch_size=16,
        shuffle=False,
    ):
        """
        Logs the training data and automatically sets the config.

        :param new_file_name:
        :param path_to_file:
        :param label_column:
        :param classes_dictionary:
        :param batch_size:
        :param shuffle:
        :return:
        """
        self.train_data_conf = self.log_data(
            path_to_dset_file,
            classes_dictionary=classes_dictionary,
            batch_size=batch_size,
            label_column=label_column,
            shuffle=shuffle,
            split="train",
        )
        save_path = os.path.join(self.local_exp_path, "train_config.json")
        with open(save_path, "w") as fp:
            json.dump(self.train_data_conf, fp)

    def log_testing_data(
        self,
        path_to_dset_file,
        label_column=None,
        input_column=None,
        target_column=None,
        classes_dictionary=None,
        batch_size=16,
        shuffle=False,
    ):
        """
        logs testing data and automatically sets the config.

        :param new_file_name:
        :param path_to_file:
        :param label_column:
        :param classes_dictionary:
        :param batch_size:
        :param shuffle:
        :return:
        """
        if label_column is not None:
            self.test_data_conf = self.log_data(
                path_to_dset_file,
                classes_dictionary=classes_dictionary,
                label_column=label_column,
                batch_size=batch_size,
                shuffle=shuffle,
                split="test",
            )
        if input_column is not None and target_column is not None:
            self.test_data_conf = self.log_data(
                path_to_dset_file,
                classes_dictionary=classes_dictionary,
                batch_size=batch_size,
                shuffle=shuffle,
                split="test",
                input_column=input_column,
                target_column=target_column,
            )

        save_path = os.path.join(self.local_exp_path, "test_config.json")
        with open(save_path, "w") as fp:
            json.dump(self.test_data_conf, fp)

    def log_model(self, model=None, model_wrapper_file=None, **model_kwargs):
        """
        Saves model and makes the model config.

        :param model: Either a picklable model, or a path to a model file.
        :param model_wrapper_file: The path to the model wrapper file.
        :param model_kwargs: Any model keyword arguments
        :return: Saves model, and makes model json.
        """
        model_file_res = model_wrapper_file
        model_res = model

        # if model not hosted on s3 or minio, upload to minio
        if not model_wrapper_file.startswith(("s3://", "gs://", "minio://")):
            model_file_res = minio_upload(
                model_wrapper_file,
                upload_url=self.minio_url,
                project=self.project_name,
                dataset=self.dataset_name,
                model=self.model_name,
                minio_user=self.minio_user,
                minio_pass=self.minio_pass,
            )
            if model is not None and not model.startswith(
                ("s3://", "gs://", "minio://")
            ):
                model_res = minio_upload(
                    model,
                    upload_url=self.minio_url,
                    project=self.project_name,
                    dataset=self.dataset_name,
                    model=self.model_name,
                    minio_user=self.minio_user,
                    minio_pass=self.minio_pass,
                )
        if model is None:
            self.model_config = {
                "name": self.model_name,
                "path_to_model_file": model_file_res,
            }
        else:
            self.model_config = {
                "name": self.model_name,
                "path_to_model_file": model_file_res,
                "model_args_dict": {**model_kwargs, "model_file": model_res},
            }

        save_path = os.path.join(self.local_exp_path, "model_config.json")

        with open(save_path, "w") as fp:
            json.dump(self.model_config, fp)

    def log_custom_evaluator(self, custom_eval_path, custom_evaluator_args):
        if not custom_eval_path.startswith(("s3://", "gs://", "minio://")):
            custom_res = minio_upload(
                custom_eval_path,
                upload_url=self.minio_url,
                project=self.project_name,
                dataset=self.dataset_name,
                model=self.model_name,
                minio_user=self.minio_user,
                minio_pass=self.minio_pass,
            )
            custom_eval_path = custom_res

        self.custom_evaluator = {
            "custom_evaluator_function": custom_eval_path,
            "custom_evaluator_args": custom_evaluator_args,
        }
        save_path = os.path.join(self.local_exp_path, "custom_config.json")

        with open(save_path, "w") as fp:
            json.dump(self.custom_evaluator, fp)

    def log_docker_metadata(self, docker_image, docker_secret_name, image_pull_policy):
        """
        Logs the docker image metadata for use during evaluation.
        :param docker_image: a valid docker image tag
        :param docker_secret_name: the env var that stores the docker pull secret in cluster
        :param image_pull_policy: the pull policy for the image
        """
        docker_meta = {
            "docker_metadata": {
                "docker_image_url": docker_image,
                "docker_secret_name": docker_secret_name,
                "image_pull_policy": image_pull_policy,
            }
        }
        self.docker_metadata = docker_meta
        save_path = os.path.join(self.local_exp_path, "docker_config.json")
        with open(save_path, "w") as fp:
            json.dump(self.docker_metadata, fp)

    def log_k8s_metadata(self, k8s_meta_dict):
        """
        Logs the metadata regarding the newly spawned k8s container. You can customize this as you see fit or just use the config that we use.
        :param k8s_meta_dict: dict containing all the data regarding the instantiation of a new kubernetes pod
        """
        k8s_meta = {"k8s_metadata": k8s_meta_dict}
        self.k8s_metadata = k8s_meta
        save_path = os.path.join(self.local_exp_path, "k8s_config.json")
        with open(save_path, "w") as fp:
            json.dump(self.k8s_metadata, fp)

    def log_attacks(self, attacks=None):
        """
        Creates the attacks json either by copying a json or by a dictionary.

        :param attacks: Either a dictionary or the path to a JSON.
        :return:
        """
        if attacks is None:
            self.attacks = False
        elif type(attacks) == str:
            self.attacks = True
            shutil.copyfile(attacks, os.path.join(self.local_exp_path, "attacks.json"))
        elif type(attacks) == dict:
            save_path = os.path.join(self.local_exp_path, "attacks.json")
            self.attacks = True
            with open(save_path, "w") as fp:
                json.dump(attacks, fp)

    def log_checks(self, checks):
        if type(checks) == str:
            if checks.split(".")[-1] == "json":
                self._set_checks_from_path(checks)
            else:
                self.checks_list.append(checks)
        elif type(checks) == dict:
            self.checks_list.append(checks)
        elif type(checks) == list:
            for i in checks:
                self.checks_list.append(i)

    def reset(self):
        """
        Resets the internal values.
        :return:
        """
        self.base = {}
        self.attack_list = []
        self.checks_list = []
        self.test_data_conf = None
        self.train_data_conf = None
        self.custom_checks = None
        self.custom_eval = None
        self.custom_eval_kwargs = None

    def create_auth(self, project_name=None, dataset_name=None):
        auth = {}
        auth["api_endpoint"] = self.api_endpoint
        auth["auth_keys"] = self.auth_keys
        auth["secrets"] = self.secrets
        if project_name == None:
            auth["project_name"] = self.project_name
            auth["dataset_name"] = self.dataset_name
        else:
            auth["project_name"] = project_name
            auth["dataset_name"] = dataset_name
        return auth

    def construct_base_config(
        self, audit=True, run_attacks_from_profile=True, task_type=None
    ):
        base_conf = {}
        base_conf["test_run_name"] = self.experiment_name
        base_conf["task_type"] = task_type
        base_conf["audit"] = audit
        if task_type == "tabular":
            base_conf["run_attacks_from_model_profile"] = run_attacks_from_profile
        if self.test_data_conf is not None:
            """
            if data file path is local, upload to minio, return the path to the minio upload as well to replace in config
            """
            base_conf["test_dataset"] = self.local_exp_path + "test_config.json"
        if self.train_data_conf is not None:
            """
            if data file path is local, upload to minio, return the path to the minio upload as well to replace in config
            """
            base_conf["train_dataset"] = self.local_exp_path + "train_config.json"
        base_conf["model"] = self.local_exp_path + "model_config.json"
        if self.custom_evaluator is not None:
            base_conf["custom_evaluator_function"] = self.custom_evaluator.get(
                "custom_evaluator_function"
            )
            base_conf["custom_evaluator_args"] = self.custom_evaluator.get(
                "custom_evaluator_args"
            )
        auth_dict = self.create_auth()
        save_path = os.path.join(self.local_exp_path, "auth.json")
        with open(save_path, "w") as fp:
            json.dump(auth_dict, fp)
        base_conf["auth_config"] = self.local_exp_path + "auth.json"
        base_save_path = os.path.join(self.local_exp_path, "base.json")
        base_conf["docker_metadata"] = self.docker_metadata["docker_metadata"]
        if self.k8s_metadata is not None:
            base_conf["k8s_metadata"] = self.k8s_metadata

        with open(base_save_path, "w") as fp:
            json.dump(base_conf, fp)
        print("configs constructed!")

    def upload_experiment(self, delete_after_upload=False):
        # change this to send with tsdk to auth config api endpoint
        self.handler.upload_folder_contents(self.local_exp_path, self.experiment_name)

    def set_auth(self, experiment):
        # used to set the authentication after pulling
        local_path = os.path.join(self.local, experiment)
        auth_path = os.path.join(local_path, "auth.json")
        with open(auth_path, "r") as fp:
            current_auth = json.load(fp)
            current_auth["auth_keys"] = self.auth_keys
        with open(auth_path, "w") as fp:
            json.dump(current_auth, fp)

    def _set_attacks_from_path(self, path):
        attack_dict = json.load(path)
        self.attack_list = self.attack_list + attack_dict["attacks"]

    def _set_checks_from_path(self, path):
        checks_dict = json.load(path)
        self.checks_list = self.checks_list + checks_dict["integrity_checks"]

    def set_custom_eval(self, file_path, args_dict=None):
        shutil.copyfile(
            file_path, os.path.join(self.local_exp_path, "custom_attacks.py")
        )
        self.custom_eval = "./custom_attacks.py"
        self.custom_eval_kwargs = args_dict

    def set_custom_checks(self, file_path):
        shutil.copyfile(
            file_path, os.path.join(self.local_exp_path, "custom_checks.py")
        )
        self.custom_checks = "./custom_checks.py"

    def set_integrity_checks(self):
        # TODO
        pass

    def run_troj_evaluation(self, project, dataset, model, no_ssl=False):
        import os
        from trojsdk.core.client_utils import submit_evaluation

        exp_name = "{}/{}/{}/".format(project, dataset, model)
        folder = os.path.join(self.local, exp_name)
        abs_path = os.path.abspath(folder)
        # config, docker_metadata, k8s_metadata = client_utils.config_from_dict(config_dict)
        return submit_evaluation(path_to_config=abs_path + "/base.json", nossl=no_ssl)

    def dump_auth(self):
        return {
            "api_endpoint": self.api_endpoint,
            "project_name": self.project_name,
            "dataset_name": self.dataset_name,
            "auth_keys": self.auth_keys,
            "secrets": self.secrets,
        }

    def run_all_experiments_from_dataset(self, project, dataset):
        dset_name = "{}/{}/".format(project, dataset)
        experiments = self.handler.get_experiment_folders(dset_name)
        for i, exp in enumerate(experiments):
            print("running experiment {} of {}".format(i + 1, len(experiments)))
            exp_folder = "/".join(exp) + "/"
            # print(exp_folder)
            self.pull_experiment(exp_folder)
            self.run_troj_evaluation(exp[0], exp[1], exp[2])
