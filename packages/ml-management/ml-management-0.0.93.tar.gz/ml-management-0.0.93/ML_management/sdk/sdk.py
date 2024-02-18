"""SDK for client library."""
import json
import posixpath
import sys
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote

import matplotlib.pyplot as plt
import pandas as pd
import websocket
from jsf import JSF
from sgqlc.operation import Operation

from ML_management.executor_template.executor_pattern import JobExecutorPattern
from ML_management.mlmanagement import get_server_url, get_server_websocket_url
from ML_management.mlmanagement.session import AuthSession
from ML_management.models.model_type_to_methods_map import ModelMethodName
from ML_management.registry.registry_manager import RegistryManager
from ML_management.sdk import schema
from ML_management.sdk.schema import ExecutionJob, ModelVersion

MODEL_INPUT_EXAMPLE = """{
    "role": "role_one",
    "model": {
        "name": "model_1_name",
        "version": 1,  # Optional. Default: latest version
    },
    "params": [{"method_one": {key1: value1, key2: value2}},
            {"method_two": {key1: value1, key2: value2}}],
    "new_model_name": "some_name"  # Optional. Default: None
}"""


def _to_datetime(df: pd.DataFrame, column_names: List[str]) -> pd.DataFrame:
    """
    Convert df's columns to datetime.

    Parameters
    ----------
    df: pd.DataFrame
        pd.DataFrame in which the columns will be converted.
    column_names: List[str]
        Сolumn names to be converted.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with converted columns.
    """
    for column_name in column_names:
        df[column_name] = pd.to_datetime(df[column_name], unit="s")

    return df


def send_graphql_request(op: Operation, json_response: bool = True) -> Any:
    """Send request to server and process the response."""
    json_data = AuthSession().sgqlc_request(op)
    if "data" not in json_data or json_data["data"] is None:
        error_message = json_data["errors"][0]["message"]
        if (
            ("extensions" in json_data["errors"][0])
            and ("params" in json_data["errors"][0]["extensions"])
            and (json_data["errors"][0]["extensions"]["params"] is not None)
            and ("message" in json_data["errors"][0]["extensions"]["params"])
        ):
            error_extensions_message = json_data["errors"][0]["extensions"]["params"]["message"]
            raise Exception(f"{error_message}\nMessage: {error_extensions_message}")
        else:
            raise Exception(error_message)

    if json_response:
        return json_data["data"]
    else:
        return op + json_data


def list_model() -> pd.DataFrame:
    """
    List available models.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with list of available models.
    """
    op = Operation(schema.Query)
    op.list_model.name()
    op.list_model.description()
    op.list_model.creation_timestamp()
    op.list_model.last_updated_timestamp()
    json_data = send_graphql_request(op)
    df = pd.DataFrame.from_dict(json_data["listModel"])
    if not df.empty:
        df = _to_datetime(df, ["creationTimestamp", "lastUpdatedTimestamp"])
    return df


def available_metrics(job_name: str) -> List[str]:
    """
    List logged types of logged metrics in given job.

    Parameters
    ----------
    job_name: str
        Name of the job.

    Returns
    -------
    List[str]
        List with names of metrics.
    """
    op = Operation(schema.Query)
    base = op.job_from_name(name=job_name)
    base.available_metrics()
    job = send_graphql_request(op, False)

    return job.job_from_name.available_metrics


def metric_history(job_name: str, metric_name: str) -> (List[float], List[float]):
    """
    Lists history of given metric in given job and plots graph of metric's change over time.

    Parameters
    ----------
    job_name: str
        Name of the job.
    metric_name: str
        Name of the metric.

    Returns
    -------
    Tuple(List[float], List[float])
        First list with timestamps of logged metric in seconds, starting with 0.
        Second list with values of metrics.
    Also plots graph using timestamps as x axis and metric's values as y axis.
    """
    op = Operation(schema.Query)
    base = op.job_from_name(name=job_name)
    base.metric_history(metric=metric_name)
    job = send_graphql_request(op, False)
    metrics = job.job_from_name.metric_history
    metrics = sorted(metrics, key=lambda x: x.timestamp)
    start_timestamp = metrics[0].timestamp
    time = [(metric.timestamp - start_timestamp) / 1000 for metric in metrics]
    metric_values = [metric.value for metric in metrics]

    plt.xlabel("seconds")
    plt.ylabel(metric_name)
    plt.plot(time, metric_values)

    return time, metric_values


def list_dataset_loader() -> pd.DataFrame:
    """
    List available dataset_loaders.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with list of available dataset_loaders.
    """
    op = Operation(schema.Query)
    op.list_dataset_loader.name()
    op.list_dataset_loader.description()
    op.list_dataset_loader.creation_timestamp()
    op.list_dataset_loader.last_updated_timestamp()
    json_data = send_graphql_request(op)
    df = pd.DataFrame.from_dict(json_data["listDatasetLoader"])
    if not df.empty:
        df = _to_datetime(df, ["creationTimestamp", "lastUpdatedTimestamp"])
    return df


def list_executor() -> pd.DataFrame:
    """
    List available executors.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with list of available executors.
    """
    op = Operation(schema.Query)
    op.list_executor.name()
    op.list_executor.description()
    op.list_executor.creation_timestamp()
    op.list_executor.last_updated_timestamp()
    json_data = send_graphql_request(op)
    df = pd.DataFrame.from_dict(json_data["listExecutor"])
    if not df.empty:
        df = _to_datetime(df, ["creationTimestamp", "lastUpdatedTimestamp"])
    return df


def add_ml_job_single_model(
    job_executor_name: str,
    executor_params: dict,
    dataset_loader_name: str,
    dataset_params: dict,
    model_name: str,
    model_params: List[Dict[str, dict]],
    collector_params: dict,
    gpu: bool = False,
    job_executor_version: Optional[int] = None,
    dataset_loader_version: Optional[int] = None,
    model_version: Optional[int] = None,
    new_model_name: Optional[str] = None,
    new_model_description: Optional[str] = None,
    experiment_name: str = "Default",
    collector_name: str = "s3",
    choice_criteria: str = "latest",
    cron_expression: Optional[str] = None,
    periodic_type: str = "ONCE",
    metric_name: Optional[str] = None,
    optimal_min: bool = False,
    additional_system_packages: Optional[List[str]] = None,
) -> str:
    """
    Create execution job.

    Parameters
    ----------
    job_executor_name: str
        Name of the executor that will execute the job.
    executor_params: Dict[str, ...]
        Dictionary of executor parameters. Example: {'executor_param1': list,
                                                     'executor_param2': int,
                                                     'executor_param3': dict,
                                                     ...}
    dataset_loader_name: str
        Name of the DatasetLoader that the model will use.
    dataset_params: dict
        Dictionary of DatasetLoader parameters.
    model_name: str
        Name of the model to interact with.
    model_params: List[Dict[str, dict]]
        List of dictionaries with parameters of model methods. Example: [{"method_one": {key1: value1, key2: value2}},
                                                                         {"method_two": {key1: value1, key2: value2}}]
    collector_params: dict
        Dictionary of collector parameters. Example: {'collector_param1': list,
                                                      'collector_param2': int,
                                                      'collector_param3': dict,
                                                     ...}
    gpu: bool = False
        Whether to use GPU for this job or not. Default: False
    job_executor_version: Optional[int] = None
        Version of the executor that will execute the job. Default: None, "latest" version is used.
    dataset_loader_version: Optional[int] = None
        Version of the DatasetLoader that the model will interact with. Default: None, "latest" version is used.
    model_version: Optional[int] = None
        Version of the model to interact with. Default: None, "latest" version is used.
    new_model_name: Optional[str] = None
        Name of the model to save in case new model is to be created as a result of job execution
        (regulated by executor.upload_model_mode). Default: None.
    new_model_description: Optional[str] = None
        Description of the new model name. Default: None.
    experiment_name: str = "Default"
        Name of the experiment. Default: "Default"
    collector_name: {"s3", }
        Name of the collector to interact with. Default: "s3"
    choice_criteria: {"latest", "initial", "best"}
        Criteria to choose the model to interact with. Required if model_version is not specified. Default: "latest"
        If "best": according to the optimal_min value, minimum (or maximum) value for the selected metric_name is taken
    cron_expression: str = None
        Cron expression for periodic or deferred jobs. Default: None
    periodic_type: {"ONCE", "PERIODIC"}
        Frequency of the task. Default: "ONCE"
    metric_name: str = None
        Name of the metric(must be logged in) for choice_criteria. Default: None
    optimal_min: bool = False
        Whether to take minimum or maximum value for the selected choice_criteria and metric_name. Default: False
    additional_system_packages: Optional[List[str]] = None
        List of system libraries for Debian family distributions that need to be installed in the job. Default: None

    Returns
    -------
    str
        Name of the Job.
    """
    models = [
        {
            "role": JobExecutorPattern.DEFAULT_ROLE,
            "model": {
                "name": model_name,
                "version": model_version,
                "choice_criteria": choice_criteria,
                "metric_name": metric_name,
                "optimal_min": optimal_min,
            },
            "params": model_params,
            "new_model_name": new_model_name,
            "description": new_model_description,
        }
    ]

    return add_ml_job(
        job_executor_name=job_executor_name,
        executor_params=executor_params,
        dataset_loader_name=dataset_loader_name,
        dataset_params=dataset_params,
        models=models,
        collector_params=collector_params,
        gpu=gpu,
        job_executor_version=job_executor_version,
        dataset_loader_version=dataset_loader_version,
        experiment_name=experiment_name,
        collector_name=collector_name,
        cron_expression=cron_expression,
        periodic_type=periodic_type,
        additional_system_packages=additional_system_packages,
    )


def add_ml_job(
    job_executor_name: str,
    executor_params: dict,
    dataset_loader_name: str,
    dataset_params: dict,
    models: List[dict],
    collector_params: dict,
    gpu: bool = False,
    job_executor_version: Optional[int] = None,
    dataset_loader_version: Optional[int] = None,
    experiment_name: str = "Default",
    collector_name: str = "s3",
    cron_expression: Optional[str] = None,
    periodic_type: str = "ONCE",
    additional_system_packages: Optional[List[str]] = None,
) -> str:
    """
    Create execution job.

    Parameters
    ----------
    job_executor_name: str
        Name of the executor that will execute the job.
    executor_params: Dict[str, ...]
        Dictionary of executor parameters. Example: {'executor_param1': list,
                                                     'executor_param2': int,
                                                     'executor_param3': dict,
                                                     ...}
    dataset_loader_name: str
        Name of the DatasetLoader that the model will use.
    dataset_params: dict
        Dictionary of DatasetLoader parameters.
    models = List[dict]
        Necessary information for using the model.
        Example:
            [
                {
                    "role": "role_one",
                    "model": {
                        "name": "model_1_name",
                        "version": 1,  # Optional. Default: latest version
                    },
                    "params": [{"method_one": {key1: value1, key2: value2}},
                               {"method_two": {key1: value1, key2: value2}}],
                    "new_model_name": "some_name"  # Optional. Default: None
                    "description": "some_description" # Optional. Default: None
                },
                {
                    "role": "role_two",
                    "model": {
                        "name": "model_2_name",
                    },
                    "params": [{"method_one": {key1: value1, key2: value2}},
                               {"method_two": {key1: value1, key2: value2}}]
                },
            ]
    collector_params: dict
        Dictionary of collector parameters. Example: {'collector_param1': list,
                                                      'collector_param2': int,
                                                      'collector_param3': dict,
                                                      ...}
    gpu: bool = False
        Whether to use GPU for this job or not. Default: False
    job_executor_version: Optional[int] = None
        Version of the executor that will execute the job. Default: None, "latest" version is used.
    dataset_loader_version: Optional[int] = None
        Version of the DatasetLoader that the model will interact with. Default: None, "latest" version is used.
    new_model_name: Optional[str] = None
        Name of the model to save in case new model is to be created as a result of job execution
        (regulated by executor.upload_model_mode). Default: None.
    experiment_name: str = "Default"
        Name of the experiment. Default: "Default"
    collector_name: {"s3", }
        Name of the collector to interact with. Default: "s3"
    choice_criteria: {"latest", "initial", "best"}
        Criteria to choose the model to interact with. Required if model_version is not specified. Default: "latest"
        If "best": according to the optimal_min value, minimum (or maximum) value for the selected metric_name is taken
    cron_expression: str = None
        Cron expression for periodic or deferred jobs. Default: None
    periodic_type: {"ONCE", "PERIODIC"}
        Frequency of the task. Default: "ONCE"
    metric_name: str = None
        Name of the metric(must be logged in) for choice_criteria. Default: None
    optimal_min: bool = False
        Whether to take minimum or maximum value for the selected choice_criteria and metric_name. Default: False
    additional_system_packages: Optional[List[str]] = None
        List of system libraries for Debian family distributions that need to be installed in the job. Default: None

    Returns
    -------
    str
        Name of the Job.
    """
    op = Operation(schema.Query)

    # parse models list of dict to check necessary params
    for model in models:
        if "role" not in model:
            raise Exception(f"You must pass role for each model. Example: \n{MODEL_INPUT_EXAMPLE}")
        if "model" not in model:
            raise Exception(f"You must pass model for each role. Example: \n{MODEL_INPUT_EXAMPLE}")
        if type(model["model"]) is not dict:
            raise Exception(f"Pass model information in the correct form. Example: \n{MODEL_INPUT_EXAMPLE}")
        if "name" not in model["model"]:
            raise Exception(f"You must pass name for each model. Example: \n{MODEL_INPUT_EXAMPLE}")
        if "params" not in model:
            raise Exception(f"You must pass params for each model. Example: \n{MODEL_INPUT_EXAMPLE}")
        if type(model["params"]) is not list:
            raise Exception(f"Pass model params in the correct form. Example: \n{MODEL_INPUT_EXAMPLE}")

    if dataset_loader_version is None:
        dataset_loader_version = int(
            RegistryManager().get_latest_dataset_loader_version(name=dataset_loader_name).version
        )

    dataset_loader_version_choice = schema.ObjectVersionOptionalInput(
        name=dataset_loader_name, version=dataset_loader_version
    )

    _dataset_loader_version = schema.ObjectVersionInput(name=dataset_loader_name, version=dataset_loader_version)
    dataset_collector_schema = op.dataset_loader_version_from_name_version(
        dataset_loader_version=_dataset_loader_version
    ).data_json_schema(collector_name=collector_name)
    dataset_collector_schema.dataset_loader_method_schema.schema_name()
    dataset_collector_schema.collector_method_schema.schema_name()

    dataset_loader_version_obj = send_graphql_request(op, json_response=False)

    dataset_loader_method_schema = (
        dataset_loader_version_obj.dataset_loader_version_from_name_version.data_json_schema.dataset_loader_method_schema.schema_name  # noqa: E501
    )
    collector_method_schema = (
        dataset_loader_version_obj.dataset_loader_version_from_name_version.data_json_schema.collector_method_schema.schema_name  # noqa: E501
    )

    dataset_loader_method_params = schema.MethodParamsInput(
        method_name=dataset_loader_method_schema,
        method_params=json.dumps(dataset_params),
    )

    collector_method_params = schema.MethodParamsInput(
        method_name=collector_method_schema, method_params=json.dumps(collector_params)
    )

    data_params = schema.DataParamsInput(
        dataset_loader_version_choice=dataset_loader_version_choice,
        collector_name=collector_name,
        dataset_loader_method_params=dataset_loader_method_params,
        collector_method_params=collector_method_params,
    )

    if job_executor_version is None:
        job_executor_version = int(RegistryManager().get_latest_executor_version(name=job_executor_name).version)

    op = Operation(schema.Query)
    _executor_version = schema.ObjectVersionInput(name=job_executor_name, version=job_executor_version)

    executor_version_choice = schema.ObjectVersionOptionalInput(name=job_executor_name, version=job_executor_version)

    executor_model_schema = op.executor_version_from_name_version(executor_version=_executor_version)
    executor_model_schema.executor_method_schema_name()

    executor_version_obj = send_graphql_request(op, json_response=False)
    executor_method_schema = executor_version_obj.executor_version_from_name_version.executor_method_schema_name

    executor_method_params = schema.MethodParamsInput(
        method_name=executor_method_schema, method_params=json.dumps(executor_params)
    )

    list_role_model_params = []

    for model in models:
        version = model["model"].get("version") or int(
            RegistryManager().get_latest_model_version(name=model["model"]["name"]).version
        )

        choice_criteria = model["model"].get("choice_criteria", "latest")

        metric_name = model["model"].get("metric_name")

        optimal_min = model["model"].get("optimal_min", False)

        model_version_choice = schema.ModelVersionChoice(
            name=model["model"]["name"],
            version=version,
            choice_criteria=choice_criteria,
            metric_name=metric_name,
            optimal_min=optimal_min,
        )

        model_methods_params = []

        for item in model["params"]:
            for key in item:
                model_methods_params.append(
                    schema.MethodParamsInput(method_name=key, method_params=json.dumps(item[key]))
                )

        new_model_name = model.get("new_model_name")
        new_model_description = model.get("description")

        current_model_params = schema.ModelParamsInput(
            model_version_choice=model_version_choice,
            list_model_method_params=model_methods_params,
            new_model_name=new_model_name,
            description=new_model_description,
        )

        model_role = schema.RoleModelParamsInput(role=model["role"], model_params=current_model_params)

        list_role_model_params.append(model_role)

    executor_params = schema.ExecutorParamsInput(
        executor_method_params=executor_method_params,
        executor_version_choice=executor_version_choice,
    )

    op = Operation(schema.Mutation)
    mutation = op.add_ml_job(
        form=schema.JobParameters(
            executor_params=executor_params,
            list_role_model_params=list_role_model_params,
            data_params=data_params,
            experiment_name=experiment_name,
            cron_expression=cron_expression,
            periodic_type=periodic_type,
            gpu=gpu,
            additional_system_packages=additional_system_packages,
        )
    )

    mutation.name()

    job = send_graphql_request(op, json_response=False)

    return job.add_ml_job.name


def job_by_name(name: str) -> ExecutionJob:
    """
    Return Job object by name.

    Parameters
    ----------
    name: str
        Name of the job.

    Returns
    -------
    Job
        Instance of the Job class.
    """
    op = Operation(schema.Query)

    base_query = op.job_from_name(name=name)
    base_query.name()
    base_query.periodic_type()
    base_query.status()
    base_query.registration_timestamp()
    base_query.start_timestamp()
    base_query.end_timestamp()
    base_query.build_job()
    base_query.exception()

    job = send_graphql_request(op, json_response=False)

    return job.job_from_name


def job_metric_by_name(name: str) -> pd.DataFrame:
    """
    Job's most recent logged metrics.

    Parameters
    ----------
    name: str
        Name of the job.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with latest metrics.
    """
    op = Operation(schema.Query)

    op.job_from_name(name=name).run.latest_metrics()
    json_data = send_graphql_request(op)

    json_data = json_data["jobFromName"]["run"]["latestMetrics"] if json_data["jobFromName"]["run"] else None

    return pd.DataFrame([json_data])


def list_model_version(name: str) -> pd.DataFrame:
    """
    List available versions of the model with such name.

    Parameters
    ----------
    name: str
        Name of the model.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with a list of available model versions.
    """
    op = Operation(schema.Query)
    base_query = op.model_from_name(name=name).list_model_version
    base_query.version()
    base_query.creation_timestamp()
    base_query.status()
    json_data = send_graphql_request(op)

    df = pd.DataFrame.from_dict(json_data["modelFromName"]["listModelVersion"])
    df = _to_datetime(df, ["creationTimestamp"])

    return df.sort_values(by=["version"], ignore_index=True)


def list_dataset_loader_version(name: str) -> pd.DataFrame:
    """
    List available versions of the dataset_loader with such name.

    Parameters
    ----------
    name: str
        Name of the DatasetLoader.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with a list of available dataset_loader versions.
    """
    op = Operation(schema.Query)
    base_query = op.dataset_loader_from_name(name=name).list_dataset_loader_version
    base_query.version()
    base_query.creation_timestamp()
    base_query.status()
    json_data = send_graphql_request(op)

    df = pd.DataFrame.from_dict(json_data["datasetLoaderFromName"]["listDatasetLoaderVersion"])
    df = _to_datetime(df, ["creationTimestamp"])

    return df.sort_values(by=["version"], ignore_index=True)


def list_executor_version(name: str) -> pd.DataFrame:
    """
    List available versions of the executor with such name.

    Parameters
    ----------
    name: str
        Name of the executor.

    Returns
    -------
    pd.DataFrame
        Pandas dataframe with a list of available executor versions.
    """
    op = Operation(schema.Query)
    base_query = op.executor_from_name(name=name).list_executor_version
    base_query.version()
    base_query.creation_timestamp()
    base_query.status()
    json_data = send_graphql_request(op)

    df = pd.DataFrame.from_dict(json_data["executorFromName"]["listExecutorVersion"])
    df = _to_datetime(df, ["creationTimestamp"])

    return df.sort_values(by=["version"], ignore_index=True)


def model_version_metainfo(model_name: str, model_version: Optional[int] = None) -> ModelVersion:
    """
    Meta information about the model version by the model name and version.

    Parameters
    ----------
    model_name: str
        Name of the model.
    model_version: Optional[int] = None
        Version of the model. Default: None, "latest" version is used.

    Returns
    -------
    ModelVersion
        ModelVersion instance with meta information.
    """
    if model_version is None:
        model_version = int(RegistryManager().get_latest_model_version(name=model_name).version)

    op = Operation(schema.Query)
    _model_version = schema.ObjectVersionInput(name=model_name, version=model_version)
    base_query = op.model_version_from_name_version(model_version=_model_version)
    base_query.name()
    base_query.version()
    base_query.status()
    base_query.build_job().status()
    base_query.build_job().docker_image_tag()
    base_query.available_executor_versions.name()
    base_query.available_executor_versions.version()
    model_version = send_graphql_request(op, json_response=False)
    return model_version.model_version_from_name_version


def rebuild_model_version_image(model_name: str, model_version: int) -> str:
    """
    Start building new docker image for specified model version.

    Parameters
    ----------
    model_name: str
        Name of the model.
    model_version: int
        Version of the model

    Returns
    -------
    str
        name of new docker image for specified model version.
    """
    op = Operation(schema.Mutation)
    _model_version = schema.ObjectVersionInput(name=model_name, version=model_version)
    op.rebuild_model_version_image(model_version=_model_version)
    result = send_graphql_request(op=op)
    return result["rebuildModelVersionImage"]


def _generate_fake_schema(json_schema: dict) -> dict:
    if "required" not in json_schema.keys():
        return {}

    required_properties = {key: json_schema["properties"][key] for key in json_schema["required"]}
    json_schema["properties"] = required_properties

    faker = JSF(json_schema)
    fake_json = faker.generate()
    return fake_json


def _print_params_by_schema(json_schema: Dict, schema_type: str) -> None:
    """Print entity JSON Schema and example with required params."""
    properties_and_required_dict = {key: json_schema[key] for key in ("properties", "required") if key in json_schema}

    json_formatted_str = json.dumps(properties_and_required_dict, indent=2)

    print(f"{schema_type} json-schema:")

    print(json_formatted_str)

    print(f"{schema_type} parameters example:")

    fake_json = _generate_fake_schema(json_schema)

    print(fake_json)


def _get_model_schema_for_executor(executor_name: str, executor_version: Optional[int], models: list) -> dict:
    if executor_version is None:
        executor_version = int(RegistryManager().get_latest_executor_version(name=executor_name).version)

    role_models = []

    for model in models:
        model_name = model["name"]
        model_version = model.get("version") or int(RegistryManager().get_latest_model_version(name=model_name).version)
        model_role = model.get("role", JobExecutorPattern.DEFAULT_ROLE)

        current_model = schema.ObjectVersionInput(name=model_name, version=model_version)
        current_role = schema.RoleModelVersionInput(role=model_role, model=current_model)

        role_models.append(current_role)

    op = Operation(schema.Query)

    _executor_version = schema.ObjectVersionInput(name=executor_name, version=executor_version)
    base_query = (
        op.executor_version_from_name_version(executor_version=_executor_version)
        .job_json_schema(models=role_models)
        .list_role_model_method_schemas
    )

    base_query.role()
    base_query.list_model_method_schemas.schema_name()
    base_query.list_model_method_schemas.json_schema()

    json_data = send_graphql_request(op)
    return json_data["executorVersionFromNameVersion"]["jobJsonSchema"]["listRoleModelMethodSchemas"]


def print_model_schema_for_executor(
    executor_name: str, models: List[dict], executor_version: Optional[int] = None
) -> None:
    """
    Print model schema for particular executor.

    Parameters
    ----------
    executor_name: str
        Name of the executor.
    models: List[dict]
        Necessary information about the model. Example1: [{"name": str = "simple_model"}];

                                               Example2: [{"name": str = "model_name1",
                                                           "role": Optional[str] = "role1",
                                                           "version": Optional[int] = version},
                                                          {"name": str = "model_name2",
                                                           "role": Optional[str] = "role2",
                                                           "version": Optional[int] = version}]
    executor_version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.
    """
    models_methods_schemas = _get_model_schema_for_executor(
        executor_name=executor_name,
        executor_version=executor_version,
        models=models,
    )
    for model_methods_schemas in models_methods_schemas:
        role = model_methods_schemas["role"]
        for model in models:
            if ("role" in model and model["role"] == role) or "role" not in model:
                model_name = model["name"]

        print(f"Model name: {model_name}, model role: {role}")
        for model_methods_schema in model_methods_schemas["listModelMethodSchemas"]:
            _print_params_by_schema(
                model_methods_schema["jsonSchema"], ModelMethodName(model_methods_schema["schemaName"]).name
            )
        print()


def generate_model_params_for_executor(
    executor_name: str, models: List[dict], executor_version: Optional[int] = None
) -> Union[List[Dict[str, dict]], List[dict]]:
    """
    Return example of model's methods parameters for executor.

    Parameters
    ----------
    executor_name: str
        Name of the executor.
    models: List[dict]
        Necessary information about the model. Example1: [{"name": str = "simple_model"}];

                                               Example2: [{"name": str = "model_name1",
                                                           "role": Optional[str] = "role1",
                                                           "version": Optional[int] = version},
                                                          {"name": str = "model_name2",
                                                           "role": Optional[str] = "role2",
                                                           "version": Optional[int] = version}]
    executor_version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.

    Returns
    -------
    List[Dict[str, Dict]]:
        Example of model's methods parameters in case simple executor.
        Example output: [{"method_one": {key1: value1, key2: value2}},
                         {"method_two": {key1: value1, key2: value2}}]
    List[dict]:
        Example of models parameter for add_ml_job function.
        Example:
            [
                {
                    "role": "role_one",
                    "model": {
                        "name": "model_1_name",
                        "version": 1,  # Optional. Default: latest version
                    },
                    "params": [{"method_one": {key1: value1, key2: value2}},
                               {"method_two": {key1: value1, key2: value2}}]
                },
                {
                    "role": "role_two",
                    "model": {
                        "name": "model_2_name",
                    },
                    "params": [{"method_one": {key1: value1, key2: value2}},
                               {"method_two": {key1: value1, key2: value2}}]
                },
            ]

    """
    models_methods_schemas = _get_model_schema_for_executor(
        executor_name=executor_name,
        executor_version=executor_version,
        models=models,
    )

    model_parameters = []

    for model_methods_schemas in models_methods_schemas:
        list_model_params = []
        for model_methods_schema in model_methods_schemas["listModelMethodSchemas"]:
            list_model_params.append(
                {model_methods_schema["schemaName"]: _generate_fake_schema(model_methods_schema["jsonSchema"])}
            )
        if len(models_methods_schemas) == 1:
            return list_model_params
        role = model_methods_schemas["role"]
        current_dict = {}
        for model in models:
            if model["role"] == role:
                model_name = model["name"]
                model_version = model.get("version") or int(
                    RegistryManager().get_latest_model_version(name=model_name).version
                )
                break
        current_dict["role"] = role
        current_dict["model"] = {}
        current_dict["model"]["name"] = model_name
        current_dict["model"]["version"] = model_version
        current_dict["params"] = list_model_params

        model_parameters.append(current_dict)

    return model_parameters


def print_datasetloader_schema(name: str, version: Optional[int] = None) -> None:
    """
    Print DatasetLoader schema.

    Parameters
    ----------
    name: str
        Name of the DatasetLoader.
    version: Optional[int] = None
        Version of the DatasetLoader. Default: None, "latest" version is used.
    """
    if version is None:
        version = int(RegistryManager().get_latest_dataset_loader_version(name=name).version)

    op = Operation(schema.Query)
    _datasetloader_version = schema.ObjectVersionInput(name=name, version=version)
    base_query = op.dataset_loader_version_from_name_version(dataset_loader_version=_datasetloader_version)
    base_query.dataset_loader_method_schema()
    json_data = send_graphql_request(op)
    json_data = json_data["datasetLoaderVersionFromNameVersion"]["datasetLoaderMethodSchema"]
    _print_params_by_schema(json_schema=json_data, schema_type="DatasetLoader")


def print_executor_schema(name: str, version: Optional[int] = None) -> None:
    """
    Print executor schema.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.
    """
    if version is None:
        version = int(RegistryManager().get_latest_executor_version(name=name).version)
    op = Operation(schema.Query)
    executor_version = schema.ObjectVersionInput(name=name, version=version)
    base_query = op.executor_version_from_name_version(executor_version=executor_version)
    base_query.executor_method_schema()
    json_data = send_graphql_request(op)

    json_data = json_data["executorVersionFromNameVersion"]["executorMethodSchema"]
    _print_params_by_schema(json_schema=json_data, schema_type="Executor")


def print_executor_roles(name: str, version: Optional[int] = None) -> None:
    """
    Print the roles required by the executor.

    Parameters
    ----------
    name: str
        Name of the executor.
    version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.
    """
    if version is None:
        version = int(RegistryManager().get_latest_executor_version(name=name).version)
    op = Operation(schema.Query)
    executor_version = schema.ObjectVersionInput(name=name, version=version)
    base_query = op.executor_version_from_name_version(executor_version=executor_version)
    base_query.desired_model_methods()
    json_data = send_graphql_request(op)
    print(json_data["executorVersionFromNameVersion"]["desiredModelMethods"])


def _get_logs_url(params: Dict[str, Any], is_execution: bool = True, stream: bool = True) -> str:
    server_url = get_server_websocket_url() if stream else get_server_url()
    url_base = posixpath.join(server_url, "logs-api")
    job_type = "execution" if is_execution else "build"
    url_encoded_params = "&".join(f"{quote(str(key))}={quote(str(value))}" for key, value in params.items())
    local_path = f"{f'stream/{job_type}' if stream else f'filedump/{job_type}'}?{url_encoded_params}"
    return posixpath.join(url_base, local_path)


def _get_logs(is_execution: bool, params: Dict[str, Any], stream: bool = True, file_name: Optional[str] = None) -> None:
    url = _get_logs_url(params=params, stream=stream, is_execution=is_execution)
    if stream:
        ws = None
        file = sys.stdout
        try:
            ws = AuthSession().instantiate_websocket_connection(url)
            if file_name:
                file = open(file_name, "w")
            while True:
                data = ws.recv()
                if not data:
                    return
                data = json.loads(data)
                if "status" not in data or data["status"] != "OK":
                    raise RuntimeError("Internal Server Error")
                print("\n".join(data["logs"]), file=file)
        except KeyboardInterrupt:
            pass
        except websocket._exceptions.WebSocketBadStatusException:
            possible_reasons_msg = (
                "Model with that name and version does not exist or does not have build job"
                if not is_execution
                else "Job with that name does not exist"
            )
            print(
                "<Connection refused. Check your query parameters, they may be incorrect.>\n"
                "<Possible reasons:>\n"
                f"<{possible_reasons_msg}>"
            )
        except Exception as err:
            print(err)
        finally:
            if ws is not None:
                ws.close()
            if file_name:
                file.close()
        return
    with AuthSession().get(url, stream=True) as resp:
        if file_name:
            with open(file_name, "wb") as f:
                for line in resp.iter_lines():
                    if line:
                        f.writelines([line, b"\n\n"])
        else:
            for line in resp.iter_lines():
                if line:
                    print(line.decode())


def get_logs(job_name: str, stream: bool = True, file_name: Optional[str] = None) -> None:
    """
    Stream logs of the execution job by job name.

    Parameters
    ----------
    job_name: str
        Name of the execution job whose logs we want to view.
    stream: bool = True
        Stream logs or dump all available at the moment.
    file_name: Optional[str] = None
        Name of the file where to save logs. Default: None. If None prints logs to the output.
    """
    _get_logs(is_execution=True, stream=stream, file_name=file_name, params={"job_id": job_name})


def get_build_logs(
    model_name: str, model_version: Optional[int] = None, stream: bool = True, file_name: Optional[str] = None
) -> None:
    """
    Stream logs of the build job by docker image tag.

    Parameters
    ----------
    model_name: str
        The name of the model whose docker image creation logs you want to view.
    model_version: Optional[int] = None
        The version of the model whose docker image creation logs you want to view.
        Default: None, "latest" version is used.
    stream: bool = True
        Stream logs or dump all available at the moment.
    file_name: Optional[str] = None
        Name of the file where to save logs. Default: None. If None prints logs to the output.
    """
    model_version = (
        int(RegistryManager().get_latest_model_version(name=model_name).version)
        if model_version is None
        else model_version
    )
    _get_logs(
        is_execution=False,
        stream=stream,
        file_name=file_name,
        params={"model_name": model_name, "model_version": model_version},
    )


def get_required_classes_by_executor(name: str, version: Optional[int] = None) -> List[str]:
    """
    Return the names of classes for the model to be inherited from, by the name of the executor.

    Parameters
    ----------
    name: str
        Name of the executor.
    executor_version: Optional[int] = None
        Version of the executor. Default: None, "latest" version is used.

    Returns
    -------
    List[str]:
        List of model class names to be inherited from.
    """
    if version is None:
        version = int(RegistryManager().get_latest_executor_version(name=name).version)
    op = Operation(schema.Query)
    executor_version = schema.ObjectVersionInput(name=name, version=version)
    base_query = op.executor_version_from_name_version(executor_version=executor_version)
    base_query.desired_model_patterns()
    json_data = send_graphql_request(op)
    return json_data["executorVersionFromNameVersion"]["desiredModelPatterns"]
