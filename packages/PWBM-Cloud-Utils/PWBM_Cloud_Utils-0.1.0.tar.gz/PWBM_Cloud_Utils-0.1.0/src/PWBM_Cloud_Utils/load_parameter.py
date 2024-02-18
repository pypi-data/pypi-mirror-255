import requests
import json
import urllib.parse
from.cloud_utils import Cloud_Utils

def input_config(policy_id_list):
    """get config files for the policy

    Args:
        policy_name_list (_type_): a list of policy from the "stacking_order"

    Returns:
        _type_: dictionary with the key of policy name and the value of policy config
    """
    # get baseline policy parameter
    policy_configs = {}
    for item in policy_id_list[1:]:
        url = "http://wits.pwbm-api.net/policy_files/all_files_by_policy/" + str(item)
        response = requests.get(url).json()
        policy_configs[item] = convert_response_to_parameter(response)

    return policy_configs


def convert_response_to_parameter(json_response):
    policy_parameter = {}
    for item in json_response:
        policy_parameter[str(item["name"])] = json.loads(item["data"])

    return policy_parameter


def get_runtime(policy_id):
    """get runtime options from the policyrun id

    Args:
        policy_id (_type_): policyrun id

    Returns:
        _type_: json format of runtime options
    """
    url = "https://wits.pwbm-api.net/run_list/" + str(policy_id)
    return requests.get(url).json()


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


def parse_runtime_options_api(rto):
    # Read runtime options files

    # Set list of scenarios to run
    run_stacked_estimates = type(rto["stacking_order"]) is list
    scenarios = ["baseline"]

    if run_stacked_estimates:
        scenarios += rto["stacking_order"][1:]

    # Set list of years to run
    years = [year for year in range(int(rto["first_year"]), int(rto["last_year"]) + 1)]

    # Set marginal tax rate variables
    mtr_vars = rto["mtr_vars"]

    # Set variables indicating whether to run post-processing procedures
    olg_inputs = rto["olg_inputs"] == "True"
    dist_years = rto["dist_years"]

    # Set indicator for running tax calculator using numba
    numba_mode = rto["numba_mode"] == "True"

    # Set sampling rate
    sample_rate = int(rto["sample_rate"])

    # Set batch size
    batch_size = int(rto["batch_size"])

    return (
        scenarios,
        run_stacked_estimates,
        years,
        mtr_vars,
        olg_inputs,
        dist_years,
        numba_mode,
        sample_rate,
        batch_size,
    )

def get_baseline(BASELINE_ID):
    """get baseline json

    Returns:
        _type_: the base line json
    """
    baseline_url = "https://wits.pwbm-api.net/policy_files/all_files_by_policy/" + str(
        BASELINE_ID
    )
    baseline_response = requests.get(baseline_url).json()
    baseline_parameter = convert_response_to_parameter(baseline_response)
    return baseline_parameter


def get_baseline_id(args):
    if args.run_id != None:
        list_run_id = Cloud_Utils._parse_args().run_id
        url = "https://wits.pwbm-api.net/run_list/" + str(list_run_id)
        RUN = requests.get(url).json()
        RUNTIME_OPTIONS = json.loads(RUN["runtime_configuration"])
        list_policies = RUNTIME_OPTIONS["stacking_order"]
        return list_policies
    else:
        return [-1]