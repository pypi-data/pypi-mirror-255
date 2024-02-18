"""Executor template for custom executor."""
from typing import List, Optional

from ML_management.executor_template.multi_model_executor_pattern import MultiModelExecutorPattern
from ML_management.mlmanagement import mlmanagement, variables
from ML_management.mlmanagement.module_finder import ModuleFinder
from ML_management.mlmanagement.variables import EXPERIMENT_NAME_FOR_EXECUTOR
from ML_management.mlmanagement.visibility_options import VisibilityOptions


class NoModelExecutorPattern(MultiModelExecutorPattern):
    """Define job executor without model."""

    def __init__(self, executor_name: str):
        """
        Init JobExecutorPattern class.

        :param executor_name: The name of the executor
        """
        super().__init__(executor_name, {}, {})

        # That parameters will be set automatically while loading the model.
        """
        :param self.artifacts: A dictionary containing ``<name, local_path>`` entries.
        """

    def upload_executor(
        self,
        pip_requirements=None,
        description: Optional[str] = None,
        extra_pip_requirements=None,
        conda_env=None,
        artifacts: Optional[dict] = None,
        visibility: VisibilityOptions = VisibilityOptions.PRIVATE,
        extra_modules_names: Optional[List[str]] = None,
        used_modules_names: Optional[List[str]] = None,
        linter_check=True,
        start_build: bool = True,
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

        if not isinstance(self.desired_model_methods, dict) or len(self.desired_model_methods) != 0:
            raise TypeError("desired_model_methods must be empty dict")

        if not isinstance(self.upload_model_modes, dict) or len(self.desired_model_methods) != 0:
            raise TypeError("upload_model_mode_dict must be empty dict")

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
                    start_build=start_build,
                )
        except Exception as err:
            raise err
        finally:
            variables.active_experiment_name = old_experiment_name
