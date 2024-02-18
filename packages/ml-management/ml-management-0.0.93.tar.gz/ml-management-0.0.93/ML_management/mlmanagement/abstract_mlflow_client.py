"""Define abstract mlflow client."""

from abc import abstractmethod
from typing import List, Optional, Union

import pandas

from mlflow.entities import Experiment, Run
from mlflow.entities.model_registry import ModelVersion, RegisteredModel
from mlflow.store.entities import PagedList


class AbstractMlflowClient:
    """Initialize an MLflow Client."""

    @abstractmethod
    def update_registered_model(self, *args, **kwargs) -> RegisteredModel:
        """Set description for model's RegisteredModel entity."""
        raise NotImplementedError

    @abstractmethod
    def update_registered_executor(self, *args, **kwargs) -> RegisteredModel:
        """Set description for executor's RegisteredModel entity."""
        raise NotImplementedError

    @abstractmethod
    def update_registered_dataset_loader(self, *args, **kwargs) -> RegisteredModel:
        """Set description for dataset_loader's RegisteredModel entity."""
        raise NotImplementedError

    @abstractmethod
    def update_model_version(self, *args, **kwargs) -> ModelVersion:
        """Set description for model's ModelVersion entity."""
        raise NotImplementedError

    @abstractmethod
    def update_executor_version(self, *args, **kwargs) -> ModelVersion:
        """Set description for executor's ModelVersion entity."""
        raise NotImplementedError

    @abstractmethod
    def update_dataset_loader_version(self, *args, **kwargs) -> ModelVersion:
        """Set description for dataset_loader's ModelVersion entity."""
        raise NotImplementedError

    @abstractmethod
    def set_model_version_tag(self, *args, **kwargs) -> None:
        """Set model version tag."""
        raise NotImplementedError

    @abstractmethod
    def set_dataset_loader_version_tag(self, *args, **kwargs) -> None:
        """Set dataset loader version tag."""
        raise NotImplementedError

    @abstractmethod
    def set_executor_version_tag(self, *args, **kwargs) -> None:
        """Set executor version tag."""
        raise NotImplementedError

    @abstractmethod
    def get_run(self, *args, **kwargs) -> Run:
        """Get run by id."""
        raise NotImplementedError

    @abstractmethod
    def get_registered_model(self, *args, **kwargs) -> RegisteredModel:
        """Get registered model by name."""
        raise NotImplementedError

    @abstractmethod
    def get_registered_dataset_loader(self, *args, **kwargs) -> RegisteredModel:
        """Get registered dataset loader by name."""
        raise NotImplementedError

    @abstractmethod
    def get_registered_executor(self, *args, **kwargs) -> RegisteredModel:
        """Get registered executor by name."""
        raise NotImplementedError

    @abstractmethod
    def search_model_versions(self, *args, **kwargs) -> PagedList[ModelVersion]:
        """Search for model versions in backend that satisfy the filter criteria."""
        raise NotImplementedError

    @abstractmethod
    def set_terminated(self, *args, **kwargs) -> None:
        """Set a run’s status to terminated."""
        raise NotImplementedError

    @abstractmethod
    def get_model_version(self, *args, **kwargs) -> ModelVersion:
        """Get model version by model name and version number."""
        raise NotImplementedError

    @abstractmethod
    def get_dataset_loader_version(self, *args, **kwargs) -> ModelVersion:
        """Get model version by dataset loader name and version number."""
        raise NotImplementedError

    @abstractmethod
    def get_executor_version(self, *args, **kwargs) -> ModelVersion:
        """Get model version by executor name and version number."""
        raise NotImplementedError

    @abstractmethod
    def download_artifacts(self, *args, **kwargs) -> str:
        """Download an artifact file or directory from a run to a local directory, and return a local path for it."""
        raise NotImplementedError

    @abstractmethod
    def download_job_artifacts(self, *args, **kwargs) -> str:
        """Download an artifact file or directory from a job to a local directory, and return a local path for it."""
        raise NotImplementedError

    @abstractmethod
    def get_model_version_requirements(self, *args, **kwargs) -> list:
        """Get requirements of the model."""
        raise NotImplementedError

    @abstractmethod
    def get_model_version_conda_env(self, *args, **kwargs) -> dict:
        """Get conda.yaml file of the model in dictionary format."""
        raise NotImplementedError

    @abstractmethod
    def get_dataset_loader_version_requirements(self, *args, **kwargs) -> list:
        """Get requirements of the dataset loader."""
        raise NotImplementedError

    @abstractmethod
    def get_dataset_loader_version_conda_env(self, *args, **kwargs) -> dict:
        """Get conda.yaml file of the dataset loader in dictionary format."""
        raise NotImplementedError

    @abstractmethod
    def get_executor_version_requirements(self, *args, **kwargs) -> list:
        """Get requirements of the executor."""
        raise NotImplementedError

    @abstractmethod
    def get_executor_version_conda_env(self, *args, **kwargs) -> dict:
        """Get conda.yaml file of the executor in dictionary format."""
        raise NotImplementedError

    @abstractmethod
    async def get_experiment_by_name(self, *args, **kwargs) -> Optional[Experiment]:
        """Retrieve an experiment by experiment name from the backend store."""
        raise NotImplementedError

    @abstractmethod
    async def search_runs(self, *args, **kwargs) -> Union[List[Run], "pandas.DataFrame"]:
        """Search experiments that fit the search criteria."""
        raise NotImplementedError

    @abstractmethod
    def get_experiment(self, *args, **kwargs) -> Experiment:
        """Get experiment by it's id."""
        raise NotImplementedError
