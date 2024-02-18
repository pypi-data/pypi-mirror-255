"""Custom exception definition for server mlflow manager graph."""

from ML_management.mlmanagement.base_exceptions import MLMServerError


class InvalidEnumTypeError(MLMServerError):
    """Define InvalidEnumTypeError exception."""

    def __init__(self, passed_enum_values, enum_type_name):
        self.passed_enum_values = passed_enum_values
        self.enum_type_name = enum_type_name
        self.message = (
            f'Passed enum values "{", ".join(passed_enum_values)}" is invalid, must be value of Enum {enum_type_name}.'
        )

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (InvalidEnumTypeError, (self.passed_enum_values, self.enum_type_name))


class InvalidModelNameError(MLMServerError):
    """Define InvalidModelNameError exception."""

    def __init__(self, passed_name, kwarg):
        self.passed_name = passed_name
        self.kwarg = kwarg
        self.message = (
            'Passed "{kwarg}" argument value "{passed_name}" is invalid, as this model is not registered in mlflow.'
        ).format(
            kwarg=kwarg,
            passed_name=passed_name,
        )

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (InvalidModelNameError, (self.passed_name, self.kwarg))


class InvalidModelVersionError(MLMServerError):
    """Define InvalidModelVersionError exception."""

    def __init__(self, passed_name, passed_version, name_kwarg, version_kwarg):
        self.passed_version = passed_version
        self.passed_name = passed_name
        self.name_kwarg = name_kwarg
        self.version_kwarg = version_kwarg
        self.message = 'Passed "{version_kwarg}" argument value "{passed_version}" is invalid, \
            as model "{passed_name}" (passed as "{name_kwarg}" argument value) has no such version.'.format(
            passed_name=passed_name,
            passed_version=passed_version,
            name_kwarg=name_kwarg,
            version_kwarg=version_kwarg,
        )

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (
            InvalidModelVersionError,
            (
                self.passed_name,
                self.passed_version,
                self.name_kwarg,
                self.version_kwarg,
            ),
        )


class KwargNotPassedWithUploadTypeError(MLMServerError):
    """Define KwargNotPassedWithUploadTypeError exception."""

    def __init__(self, kwarg, passed_upload_model_type):
        self.passed_upload_model_type = passed_upload_model_type
        self.kwarg = kwarg
        self.message = (
            'Argument "{kwarg}" cannot be ommitted with upload_model_type UploadModelType.{passed_upload_model_type}.'
        ).format(
            kwarg=kwarg,
            passed_upload_model_type=passed_upload_model_type,
        )

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (KwargNotPassedWithUploadTypeError, (self.kwarg, self.passed_upload_model_type))


class ModelTypeIsNotFoundError(MLMServerError):
    """Define ModelTypeIsNotFoundError exception."""

    def __init__(self):
        self.message = "Model type is not found. You must inherit the desired template."

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (ModelTypeIsNotFoundError, ())


class ExistingModelWithOtherTypeError(MLMServerError):
    """Define ExistingModelWithOtherTypeError exception."""

    def __init__(self, name):
        self.name = name
        self.message = (
            f'The other model type with name "{name}" exists.'
            f"You cannot upload a model with the same name as an existing model of a different type."
        )

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (ExistingModelWithOtherTypeError, (self.name,))


class InvalidExperimentNameError(MLMServerError):
    """Define InvalidExperimentNameError exception."""

    def __init__(self, model_type, exp_name):
        self.model_type = model_type
        self.exp_name = exp_name
        self.message = f"You can't specify '{exp_name}' experiment name for model type '{model_type}' upload."

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (InvalidExperimentNameError, (self.model_type, self.exp_name))


class InvalidUploadModelModeError(MLMServerError):
    """Define InvalidUploadModelModeError exception."""

    def __init__(self, model_type, upload_mode):
        self.model_type = model_type
        self.upload_mode = upload_mode
        self.message = f"You can't specify upload mode '{upload_mode}' for '{model_type}' model."

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (InvalidUploadModelModeError, (self.model_type, self.upload_mode))


class InvalidVisibilityOptionError(MLMServerError):
    """Define InvalidVisibilityOptionError exception."""

    def __init__(self, model_type):
        self.model_type = model_type
        self.message = f"You must specify visibility option for '{model_type}'."

        super().__init__(self.message)

    def __reduce__(self):
        """Define reduce method to make exception picklable."""
        return (InvalidUploadModelModeError, (self.model_type,))
