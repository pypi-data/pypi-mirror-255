"""Executor template for custom executor."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ML_management.executor_template.upload_model_mode import UploadModelMode
from ML_management.mlmanagement import mlmanagement, variables
from ML_management.mlmanagement.module_finder import ModuleFinder
from ML_management.mlmanagement.variables import EXPERIMENT_NAME_FOR_EXECUTOR
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.models.model_type_to_methods_map import ModelMethodName
from ML_management.models.patterns.model_pattern import Model
from mlflow.pyfunc import PythonModel


class MultiModelExecutorPattern(PythonModel, ABC):
    """Define custom job executor."""

    def __init__(
        self,
        executor_name: str,
        desired_model_methods: Dict[str, List[ModelMethodName]],
        upload_model_modes: Dict[str, UploadModelMode],
    ):
        """
        Init MultiModelExecutorPattern class.

        :param executor_name: The name of the executor
        :param desired_model_methods: The dict of specify list of desired model methods for this executor
        :param upload_model_modes: How to log models after job
        """
        self.executor_name = executor_name
        self.upload_model_modes = upload_model_modes
        self.desired_model_methods = desired_model_methods

        # That parameters will be set automatically while loading the model.
        """
        :param self.artifacts: A dictionary containing ``<name, local_path>`` entries.
        """
        self.artifacts: dict = {}

        # That parameter will be set automatically in job before the 'execute' func would be executed.
        self.dataset = None
        self.role_model_map: Dict[str, Model] = {}
        self.model_method_parameters_dict: Dict[str, Dict[ModelMethodName, dict]] = {}
        self.model_method_schemas = {}
        """
        :param self.role_model_map: role to model map
        :param self.dataset: object for dataset
        :param self.model_method_parameters_dict: the dict of parameters for each desired_model_methods.
            One could use it in execute() function like that:

                def execute(self):
                    self.models["role_model"].train_function(
                        **self.models_methods_parameters["role_model"][ModelMethodName.train_function]
                    )

            In that case method 'execute' calls train_function method of the model with corresponding parameters
            for that method.
        """

    @abstractmethod
    def execute(self, **executor_params):
        """
        Do execution step.

        Parameter self.models with the desired model will be set automatically in the job before 'execute' execution.
        To get data_path use self.data_path parameter, which also will be set in the job.
        'executor_methods_params' are executor parameters. One has to define it as ordinary kwargs with type annotation.
        Also, you could use self.model_methods_parameters for call desired model method with right params.
        return param: artifacts: A dictionary containing ``<name, artifact_uri>`` entries.
                      For example, consider the following ``artifacts`` dictionary::

                        {
                            "my_file": "s3://my-bucket/path/to/my/file",
                            "my_file2": "/home/username/path/to/my/file"
                        }

                      In this case, the ``"my_file"`` artifact is downloaded from S3.
                      The ``"my_file2"`` artifact is downloaded from local path.

                      If ``None``, no artifacts are added to the model.
        """
        raise NotImplementedError

    def upload_executor(
        self,
        description: str,
        pip_requirements=None,
        extra_pip_requirements=None,
        conda_env=None,
        artifacts: Optional[dict] = None,
        visibility: VisibilityOptions = VisibilityOptions.PRIVATE,
        extra_modules_names: Optional[List[str]] = None,
        used_modules_names: Optional[List[str]] = None,
        linter_check=True,
    ):
        """
        Upload wrapper to MLmanagement server.

        :param pip_requirements: {{ pip_requirements }}

        :param extra_pip_requirements: {{ extra_pip_requirements }}
        `pip_requirements` and 'extra_pip_requirements' must be either a string path to a pip requirements file on the
            local filesystem or an iterable of pip requirement strings.

        :param conda_env: {{ conda_env }}
        'conda_env' must be a dict specifying the conda environment for this model.

        :param artifacts: A dictionary containing ``<name, artifact_uri>`` entries. Remote artifact URIs
                          are resolved to absolute filesystem paths, producing a dictionary of
                          ``<name, absolute_path>`` entries. ``python_model`` can reference these
                          resolved entries as the ``artifacts`` property of the ``context`` parameter
                          in :func:`PythonModel.load_context() <mlflow.pyfunc.PythonModel.load_context>`
                          and :func:`PythonModel.predict() <mlflow.pyfunc.PythonModel.predict>`.
                          For example, consider the following ``artifacts`` dictionary::

                            {
                                "my_file": "s3://my-bucket/path/to/my/file"
                            }

                          In this case, the ``"my_file"`` artifact is downloaded from S3. The
                          ``python_model`` can then refer to ``"my_file"`` as an absolute filesystem
                          path via ``context.artifacts["my_file"]``.

                          If ``None``, no artifacts are added to the executor.

        :param visibility: either a private or public executor.

        :param extra_modules_names: names of modules that should be pickled by value
            in addition to auto-detected modules.

        :param used_modules_names: modules that should be pickled by value, disables the auto-detection of modules.
        """
        old_experiment_name = variables.active_experiment_name

        if not isinstance(self.desired_model_methods, dict) or not all(
            isinstance(methods, list) for methods in self.desired_model_methods.values()
        ):
            raise TypeError("desired_model_methods must be Dict[str, List[ModelMethodName]]")

        desired_methods = [method for methods in self.desired_model_methods.values() for method in methods]

        if not all(isinstance(method, ModelMethodName) for method in desired_methods):
            raise TypeError("desired_model_methods must be Dict[str, List[ModelMethodName]]")

        if not isinstance(self.upload_model_modes, dict) or not all(
            isinstance(mode, UploadModelMode) for mode in self.upload_model_modes.values()
        ):
            raise TypeError("upload_model_mode_dict must be Dict[str, UploadModelMode]")

        if set(self.desired_model_methods.keys()) != set(self.upload_model_modes.keys()):
            raise KeyError("desired_model_methods and upload_model_mode must have the same model roles")

        mlmanagement.set_experiment(EXPERIMENT_NAME_FOR_EXECUTOR, visibility=VisibilityOptions.PUBLIC)
        try:
            with mlmanagement.start_run(nested=True):
                mlmanagement.log_model(
                    artifact_path="",
                    description=description,
                    artifacts=artifacts,
                    python_model=self,
                    registered_model_name=self.executor_name,
                    pip_requirements=pip_requirements,
                    extra_pip_requirements=extra_pip_requirements,
                    conda_env=conda_env,
                    visibility=visibility,
                    extra_modules_names=extra_modules_names,
                    used_modules_names=used_modules_names,
                    root_module_name=ModuleFinder.get_my_caller_module_name(),
                    linter_check=linter_check,
                )
        except Exception as err:
            raise err
        finally:
            variables.active_experiment_name = old_experiment_name
