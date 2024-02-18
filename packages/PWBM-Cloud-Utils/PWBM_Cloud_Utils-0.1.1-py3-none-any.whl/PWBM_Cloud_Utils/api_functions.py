import requests


class APIClient:
    def __init__(self):
        self.base_url = "https://wits.pwbm-api.net"

    def _make_request(self, method, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, json=data)
        return response.json()


class RunListAPI(APIClient):
    def get_run_list(self, run_list_id):
        return self._make_request("GET", f"run_list/{run_list_id}")

    def delete_run_list(self, run_list_id):
        return self._make_request("DELETE", f"run_list/{run_list_id}")

    def get_run_lists_by_model(self, model_id):
        return self._make_request("GET", f"run_list/model/{model_id}")

    def upload_run_list(self, model_id, run_list_data):
        return self._make_request(
            "POST", f"run_list/upload/{model_id}", data=run_list_data
        )

    def put_run_list(self, run_list_data):
        return self._make_request("PUT", "run_list", data=run_list_data)

    def create_run_list(self, run_list_data):
        return self._make_request("POST", "run_list", data=run_list_data)

    def execute_run_list(self, run_list_id):
        return self._make_request("POST", f"run_list/execute/{run_list_id}")

    def get_batch_job_status(self, run_list_id):
        return self._make_request("GET", f"run_list/job_status/{run_list_id}")

    def get_run_list_output(self, run_list_id):
        return self._make_request("GET", f"run_list/output/{run_list_id}")


class PolicyAPI(APIClient):
    def get_all_policies(self, model_id):
        return self._make_request("GET", f"policy/get_all/{model_id}")

    def get_policy(self, policy_id):
        return self._make_request("GET", f"policy/{policy_id}")

    def delete_policy(self, policy_id):
        return self._make_request("DELETE", f"policy/{policy_id}")

    def update_policy(self, policy_data):
        return self._make_request("PUT", "policy", data=policy_data)

    def add_policy(self, policy_data):
        return self._make_request("POST", "policy", data=policy_data)


class PolicyFilesAPI(APIClient):
    def upload_files(self, policy_id, files):
        endpoint = f"policy_files/upload/{policy_id}"
        data = {"files": files}
        return self._make_request("POST", endpoint, data)

    def create_files(self, policy_id, files):
        endpoint = f"policy_files/{policy_id}"
        data = {"files": files}
        return self._make_request("POST", endpoint, data)

    def get_all_files_by_policy(self, policy_id):
        endpoint = f"policy_files/all_files_by_policy/{policy_id}"
        return self._make_request("GET", endpoint)

    def delete_all_files_by_policy(self, policy_id):
        endpoint = f"policy_files/all_files_by_policy/{policy_id}"
        return self._make_request("DELETE", endpoint)

    def get_file(self, file_id):
        endpoint = f"policy_files/{file_id}"
        return self._make_request("GET", endpoint)

    def delete_file(self, file_id):
        endpoint = f"policy_files/{file_id}"
        return self._make_request("DELETE", endpoint)

    def delete_policy_file_link(self, policy_id, file_id):
        endpoint = "policy_files/policy_file_link"
        data = {"policy_id": policy_id, "file_id": file_id}
        return self._make_request("DELETE", endpoint, data)

    def update_file(self, file_id, file_data):
        endpoint = f"policy_files/file/{file_id}"
        return self._make_request("PUT", endpoint, data=file_data)

    def object_update_file(self, file_data):
        endpoint = "policy_files"
        return self._make_request("PUT", endpoint, data=file_data)


class ModelsAPI(APIClient):

    def get_model(self, id: int):
        return self._make_request("GET", "models/get/" + str(id))
    
    def get_all_models(self):
        return self._make_request("GET", "models/get_all")

    def create_model(self, model_data):
        return self._make_request("POST", "models", data=model_data)

    def delete_model(self, model_id):
        return self._make_request("DELETE", f"models/{model_id}")


class RunList:
    def __init__(self, name, description, runtime_configuration, model_id):
        self.data = {
            "name": name,
            "description": description,
            "runtime_configuration": runtime_configuration,
            "model_id": model_id,
        }

    def get_data(self):
        return self.data


class Policy:
    def __init__(self, name, description, model_id):
        self.data = {
            "name": name,
            "description": description,
            "model_id": model_id,
        }

    def get_data(self):
        return self.data


class ModelData:
    def __init__(
        self,
        name,
        description,
        output_bucket,
        job_queue,
        job_definition,
        compute_environment,
        ecr_registry,
    ):
        self.data = {
            "name": name,
            "description": description,
            "output_bucket": output_bucket,
            "job_queue": job_queue,
            "job_definition": job_definition,
            "compute_environment": compute_environment,
            "ecr_registry": ecr_registry,
        }

    def get_data(self):
        return self.data


run_list_api = RunListAPI()
policy_api = PolicyAPI()
policy_files_api = PolicyFilesAPI()
models_api = ModelsAPI()
