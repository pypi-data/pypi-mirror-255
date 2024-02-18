"""Map supported executor function name to infer jsonschema to tag."""
from enum import Enum

from ML_management.executor_template import multi_model_executor_pattern


class ExecutorMethodName(str, Enum):
    """Map supported executor function name to infer jsonschema."""

    execute = "executor_method"


executor_pattern_to_methods = {multi_model_executor_pattern.MultiModelExecutorPattern: [ExecutorMethodName.execute]}
