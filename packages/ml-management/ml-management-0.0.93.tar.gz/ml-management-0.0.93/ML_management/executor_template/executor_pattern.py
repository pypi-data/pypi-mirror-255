"""Executor template for custom executor."""
from typing import Dict, List

from ML_management.executor_template.multi_model_executor_pattern import MultiModelExecutorPattern
from ML_management.executor_template.upload_model_mode import UploadModelMode
from ML_management.models.model_type_to_methods_map import ModelMethodName
from ML_management.models.patterns.model_pattern import Model


class JobExecutorPattern(MultiModelExecutorPattern):
    """Define custom job executor."""

    DEFAULT_ROLE = "single"

    def __init__(
        self, executor_name: str, desired_model_methods: List[ModelMethodName], upload_model_mode: UploadModelMode
    ):
        """
        Init JobExecutorPattern class.

        :param executor_name: The name of the executor
        :param desired_model_methods: Specify list of desired model methods for this executor
        :param upload_model_mode: How to log model after job
        """
        super().__init__(
            executor_name, {self.DEFAULT_ROLE: desired_model_methods}, {self.DEFAULT_ROLE: upload_model_mode}
        )

        # That parameters will be set automatically while loading the model.
        """
        :param self.artifacts: A dictionary containing ``<name, local_path>`` entries.
        """

        # That parameters will be set automatically in job before the 'execute' func would be executed.
        """
        :param self.model_methods_parameters: the dict of parameters for each desired_model_methods.
            One could use it in execute() function like that:

                def execute(self):
                    self.model.train_function(**self.model_methods_parameters[ModelMethodName.train_function])

            In that case method 'execute' calls train_function method of the model with corresponding parameters
            for that method. See examples in default_executors folder.
        :param self.model_methods_schema: the dict of schema parameters for each desired_model_methods.
        """

    @property
    def model(self) -> Model:
        """Property returning a single model.

        :return: python model
        """
        return self.role_model_map[self.DEFAULT_ROLE]

    @model.setter
    def model(self, model):
        """Property to change the model.

        :param: python model
        """
        self.role_model_map[self.DEFAULT_ROLE] = model

    @property
    def model_methods_parameters(self) -> Dict[ModelMethodName, dict]:
        """Property for the dictionary wrapper.

        :return: the dict of parameters for each desired_model_methods
        """
        return self.model_method_parameters_dict[self.DEFAULT_ROLE]

    @property
    def model_method_schema(self) -> Dict[ModelMethodName, dict]:
        """Property for the dictionary wrapper.

        :return: schema for each desired_model_methods
        """
        return self.model_method_schemas[self.DEFAULT_ROLE]
