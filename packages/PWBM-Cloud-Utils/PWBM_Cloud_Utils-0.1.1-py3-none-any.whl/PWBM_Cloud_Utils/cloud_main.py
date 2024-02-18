from .api_functions import RunListAPI, PolicyAPI, PolicyFilesAPI, ModelsAPI
import urllib.parse
import json
import requests
import os


class Cloud_Main:
    _input_config: dict
    _runtime_option: dict
    _model_name: str
    _runlist_name: str
    _runlist_description: str
    _output_bucket: str
    _output_path: str

    _policy_files: any
    _policy_configs: any

    def __init__(
        self,
        run_id: int,
        policy_id: int,
        local: bool = True,
        merge_baseline: bool = True,
    ):
        run_list = RunListAPI()
        config = run_list.get_run_list(run_id)
        print(config)  # BatchId and JobId
        self._name = config["name"]
        self._description = config["description"]
        self._model_id = config["model_id"]
        model_api = ModelsAPI()
        model = model_api.get_model(self._model_id)
        self._input_config = json.loads(config["runtime_configuration"])
        stacking_order = self._input_config["stacking_order"]
        print(self._input_config["stacking_order"])
        policy_api = PolicyAPI().get_policy(policy_id)
        policy_files = PolicyFilesAPI().get_all_files_by_policy(policy_id)
        self._policy_files = policy_files
        self._policy_configs = self.input_config(stacking_order)
        self._output_path = f'Output\\{model["version"]}\\{run_id}\\{policy_id}'
        self._outout_bucket = model["output_bucket"]
        print("end")

    def input_config(self, policy_id_list):
        """get config files for the policy

        Args:
            policy_name_list (_type_): a list of policy from the "stacking_order"

        Returns:
            _type_: dictionary with the key of policy name and the value of policy config
        """
        # get baseline policy parameter
        policy_configs = {}
        for item in policy_id_list[1:]:
            url = "http://wits.pwbm-api.net/policy_files/all_files_by_policy/" + str(
                item
            )
            # url = "http://127.0.0.1:8008/policy_files/all_files_by_policy/" + str(item)
            response = requests.get(url).json()
            policy_configs[item] = self.convert_response_to_parameter(response)

        return policy_configs

    def save_output(policy_id, policy_name):
        """get runtime options from the policyrun id

        Args:
            policy_id . policy_name

        Returns:
            _type_: json format of runtime options
        """
        policy_name_url = urllib.parse.quote(policy_name)
        url = "https://wits.pwbm-api.net/run_list/output_details/?id={}&path={}".format(
            str(policy_id), policy_name_url
        )
        return requests.post(url).json()

    def convert_response_to_parameter(self,json_response):
        policy_parameter = {}
        for item in json_response:
            policy_parameter[str(item["name"])] = json.loads(item["data"])

        return policy_parameter

    def write_parameter_files(self, path: str) -> bool:
        if not os.path.exists(path):
            os.makedirs(path)

        for f in self._policy_files:
            if type(f['data']) is str:
                with open(os.path.join(path, f"{f['name']}.{f['file_type']}"), 'w') as wf:
                    wf.write(f['data'])
            elif type(f['data']) is bytes:
                with open(os.path.join(path, f"{f['name']}.{f['file_type']}"), 'wb') as wf:
                    wf.write(f['data'])
        
        return True

    @property
    def Input_Config(self):
        return self._input_config

    @property
    def Policy_Files(self):
        return self._policy_files

    @property
    def Name(self):
        return self._name

    @property
    def Description(self):
        return self._description

    @property
    def Model_Id(self):
        return self._model_id
    
    @property
    def Output_Path(self):
        return self._output_path

    @property
    def Output_Bucket(self):
        return self._output_bucket

    @property
    def Policy_Configs(self):
        return self._policy_configs
