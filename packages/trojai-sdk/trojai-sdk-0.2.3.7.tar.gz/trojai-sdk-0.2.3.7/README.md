# trojai-sdk

TrojAI's SDK and command line interface. This tool is used for submitting and monitoring jobs for evaluation by the TrojAI engine.

## Uses

### Command Line Functions
IMPORTANT: We've updated our authentication methods! Older auth configs required an id_token key and a refresh_token key. These keys are no longer required and should be removed from auth configs going forward. The only key required moving forward is the api_key. 

The behaviour for submitting jobs using the command line is as follows:

`Submit a valid config`
```bash
tsdk -c path/to/config.json
```
The following arguments are intended to be used together to download failed results of a given job. Any feedback on this feature is appreciated!


`Download failed samples from a given run`
```bash
tsdk -dl_fails -job_name "trojeval-tabular-24052023-142652-850205" -auth_config ".\trojsdk\examples\auth_config_dev.json" -save_path "./failed_samples.json"
```

job_name: Can be found by using kubectl get pods. K8s creates the pods with an extra tag at the end, be sure to remove the randomly generated characters that prevent pod collisions.

Example:
k8s pod name: trojeval-tabular-25052023-170036-121934-tknf5
valid job name: trojeval-tabular-25052023-170036-121934


Copy the job name of the evaluation when completed. You can also find the job name by clicking the Status column link in the front end project view for any run. 
auth_config: A path to a valid auth config for your cluster. Valid endpoint and api key are required
save_path: where the resulting json file will be saved to

### Programmatic Functions
We've added a more programmatic version of the config builder to be used in any python script. 
This TrojExperimenter is designed to be an aggregator for your trojai config files, and configs can be swapped in code instead of manually modifying json files.

A test example is detailed below:
```python
conf_handler = TrojExperimenter("./trojsdk/examples/auth_config_dev.json")
proj = "test_proj"
dataset = "credit_dataset"
model = "logistic_model"
conf_handler.create_experiment(proj, dataset, model, delete_existing=True)
conf_handler.log_testing_data(path_to_dset_file="s3://trojai-object-storage/stars_tabular/stars_validation.csv", label_column="Type", classes_dictionary= {
    "red dwarf": 0,
    "brown dwarf": 1,
    "white dwarf":  2,
    "main sequence": 3,
    "super giants": 4,
    "hyper giants": 5
})
conf_handler.log_model(model = "s3://trojai-object-storage/stars_tabular/StarKNNPipe.pkl", model_wrapper_file = "s3://trojai-object-storage/stars_tabular/StarKNNWrapper.py")
conf_handler.log_attacks("./trojsdk/examples/star_attacks.json")
conf_handler.log_docker_metadata("trojai/troj-engine-base-tabular:tabular-dev-latest", "trojaicreds", "IfNotPresent")
k8s_dict = {
        "container_port": 80,
        "resources": {
            "requests": {
                "cpu": "250m",
                "memory": "800M"
            },
            "limits": {
                "cpu": "500m",
                "memory": "2000M"
            }
        },
        "tolerations": [
            {
                "effect": "NoSchedule",
                "operator": "Equal",
                "value": "robustness-evaluation",
                "key": "dedicated"
            }
        ]
    }
conf_handler.log_k8s_metadata(k8s_dict)
conf_handler.construct_base_config(task_type="tabular")
tjh = conf_handler.run_troj_evaluation(proj, dataset, model, no_ssl=True)
```

### Config
For examples and explanations on creating valid your config files, please visit our gitbook.
<br/>[Intro to TrojAI](https://trojai.gitbook.io/trojai/)
<br/>[NLP](https://trojai.gitbook.io/trojai/nlp/configuring-your-nlp-evaluation)
<br/>[Tabular](https://trojai.gitbook.io/trojai/tabular/configuring-your-tabular-evaluation)
