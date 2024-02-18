import sgqlc.types


schema = sgqlc.types.Schema()


__docformat__ = 'markdown'


########################################################################
# Scalars and Enumerations
########################################################################
Boolean = sgqlc.types.Boolean

class DirectionInput(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `asc`None
    * `desc`None
    '''
    __schema__ = schema
    __choices__ = ('asc', 'desc')


Float = sgqlc.types.Float

ID = sgqlc.types.ID

Int = sgqlc.types.Int

class JSON(sgqlc.types.Scalar):
    '''The `JSON` scalar type represents JSON values as specified by
    [ECMA-404](http://www.ecma-
    international.org/publications/files/ECMA-ST/ECMA-404.pdf).
    '''
    __schema__ = schema


class JobStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `FAILED`None
    * `PLANNED`None
    * `RUNNING`None
    * `SUCCESSFUL`None
    '''
    __schema__ = schema
    __choices__ = ('FAILED', 'PLANNED', 'RUNNING', 'SUCCESSFUL')


class JobsSortBy(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `name`None
    * `registration_timestamp`None
    '''
    __schema__ = schema
    __choices__ = ('name', 'registration_timestamp')


class LONG(sgqlc.types.Scalar):
    '''The `LONG` scalar type represents long int type.'''
    __schema__ = schema


class ObjectSortBy(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `creation_timestamp`None
    * `name`None
    '''
    __schema__ = schema
    __choices__ = ('creation_timestamp', 'name')


class ObjectVersionSortBy(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `creation_timestamp`None
    * `name`None
    * `version`None
    '''
    __schema__ = schema
    __choices__ = ('creation_timestamp', 'name', 'version')


class PeriodicType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ONCE`None
    * `PERIODIC`None
    '''
    __schema__ = schema
    __choices__ = ('ONCE', 'PERIODIC')


String = sgqlc.types.String

class UploadModelType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `new_model`None
    * `new_version`None
    * `root`None
    '''
    __schema__ = schema
    __choices__ = ('new_model', 'new_version', 'root')



########################################################################
# Input Objects
########################################################################
class DataParamsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('dataset_loader_version_choice', 'collector_name', 'dataset_loader_method_params', 'collector_method_params')
    dataset_loader_version_choice = sgqlc.types.Field(sgqlc.types.non_null('ObjectVersionOptionalInput'), graphql_name='datasetLoaderVersionChoice')

    collector_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='collectorName')

    dataset_loader_method_params = sgqlc.types.Field(sgqlc.types.non_null('MethodParamsInput'), graphql_name='datasetLoaderMethodParams')

    collector_method_params = sgqlc.types.Field(sgqlc.types.non_null('MethodParamsInput'), graphql_name='collectorMethodParams')



class ExecutorParamsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('executor_version_choice', 'executor_method_params')
    executor_version_choice = sgqlc.types.Field(sgqlc.types.non_null('ObjectVersionOptionalInput'), graphql_name='executorVersionChoice')

    executor_method_params = sgqlc.types.Field(sgqlc.types.non_null('MethodParamsInput'), graphql_name='executorMethodParams')



class JobFilterSettings(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('periodic_type', 'status', 'init_model_version', 'dataset_loader_version', 'executor_version', 'start_interval', 'end_interval', 'job_name', 'experiment_name')
    periodic_type = sgqlc.types.Field(PeriodicType, graphql_name='periodicType')

    status = sgqlc.types.Field(JobStatus, graphql_name='status')

    init_model_version = sgqlc.types.Field('ObjectVersionInput', graphql_name='initModelVersion')

    dataset_loader_version = sgqlc.types.Field('ObjectVersionInput', graphql_name='datasetLoaderVersion')

    executor_version = sgqlc.types.Field('ObjectVersionInput', graphql_name='executorVersion')

    start_interval = sgqlc.types.Field('TimestampInterval', graphql_name='startInterval')

    end_interval = sgqlc.types.Field('TimestampInterval', graphql_name='endInterval')

    job_name = sgqlc.types.Field(String, graphql_name='jobName')

    experiment_name = sgqlc.types.Field(String, graphql_name='experimentName')



class JobParameters(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('executor_params', 'data_params', 'list_role_model_params', 'experiment_name', 'cron_expression', 'periodic_type', 'gpu', 'additional_system_packages')
    executor_params = sgqlc.types.Field(sgqlc.types.non_null(ExecutorParamsInput), graphql_name='executorParams')

    data_params = sgqlc.types.Field(sgqlc.types.non_null(DataParamsInput), graphql_name='dataParams')

    list_role_model_params = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('RoleModelParamsInput')), graphql_name='listRoleModelParams')

    experiment_name = sgqlc.types.Field(String, graphql_name='experimentName')

    cron_expression = sgqlc.types.Field(String, graphql_name='cronExpression')

    periodic_type = sgqlc.types.Field(PeriodicType, graphql_name='periodicType')

    gpu = sgqlc.types.Field(Boolean, graphql_name='gpu')

    additional_system_packages = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='additionalSystemPackages')



class JobSingleParameters(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('executor_params', 'model_params', 'data_params', 'experiment_name', 'cron_expression', 'periodic_type', 'gpu', 'additional_system_packages')
    executor_params = sgqlc.types.Field(sgqlc.types.non_null(ExecutorParamsInput), graphql_name='executorParams')

    model_params = sgqlc.types.Field(sgqlc.types.non_null('ModelParamsInput'), graphql_name='modelParams')

    data_params = sgqlc.types.Field(sgqlc.types.non_null(DataParamsInput), graphql_name='dataParams')

    experiment_name = sgqlc.types.Field(String, graphql_name='experimentName')

    cron_expression = sgqlc.types.Field(String, graphql_name='cronExpression')

    periodic_type = sgqlc.types.Field(PeriodicType, graphql_name='periodicType')

    gpu = sgqlc.types.Field(Boolean, graphql_name='gpu')

    additional_system_packages = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='additionalSystemPackages')



class JobsSortBySortingInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('sort_by', 'direction')
    sort_by = sgqlc.types.Field(sgqlc.types.non_null(JobsSortBy), graphql_name='sortBy')

    direction = sgqlc.types.Field(sgqlc.types.non_null(DirectionInput), graphql_name='direction')



class MethodParamsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('method_name', 'method_params')
    method_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='methodName')

    method_params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='methodParams')



class ModelParamsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('model_version_choice', 'list_model_method_params', 'description', 'new_model_name')
    model_version_choice = sgqlc.types.Field(sgqlc.types.non_null('ModelVersionChoice'), graphql_name='modelVersionChoice')

    list_model_method_params = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MethodParamsInput))), graphql_name='listModelMethodParams')

    description = sgqlc.types.Field(String, graphql_name='description')

    new_model_name = sgqlc.types.Field(String, graphql_name='newModelName')



class ModelVersionChoice(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('name', 'version', 'choice_criteria', 'metric_name', 'optimal_min')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    version = sgqlc.types.Field(Int, graphql_name='version')

    choice_criteria = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='choiceCriteria')

    metric_name = sgqlc.types.Field(String, graphql_name='metricName')

    optimal_min = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='optimalMin')



class ObjectFilterSettings(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('name',)
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')



class ObjectSortBySortingInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('sort_by', 'direction')
    sort_by = sgqlc.types.Field(sgqlc.types.non_null(ObjectSortBy), graphql_name='sortBy')

    direction = sgqlc.types.Field(sgqlc.types.non_null(DirectionInput), graphql_name='direction')



class ObjectVersionFilterSettings(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('version',)
    version = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='version')



class ObjectVersionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('name', 'version')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    version = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='version')



class ObjectVersionOptionalInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('name', 'version')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    version = sgqlc.types.Field(Int, graphql_name='version')



class ObjectVersionSortBySortingInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('sort_by', 'direction')
    sort_by = sgqlc.types.Field(sgqlc.types.non_null(ObjectVersionSortBy), graphql_name='sortBy')

    direction = sgqlc.types.Field(sgqlc.types.non_null(DirectionInput), graphql_name='direction')



class RoleModelParamsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('role', 'model_params')
    role = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='role')

    model_params = sgqlc.types.Field(sgqlc.types.non_null(ModelParamsInput), graphql_name='modelParams')



class RoleModelVersionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('role', 'model')
    role = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='role')

    model = sgqlc.types.Field(sgqlc.types.non_null(ObjectVersionInput), graphql_name='model')



class TimestampInterval(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('start', 'end')
    start = sgqlc.types.Field(LONG, graphql_name='start')

    end = sgqlc.types.Field(LONG, graphql_name='end')




########################################################################
# Output Objects and Interfaces
########################################################################
class BuildJob(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('start_timestamp', 'end_timestamp', 'exception', 'docker_image_tag', 'status')
    start_timestamp = sgqlc.types.Field(LONG, graphql_name='startTimestamp')

    end_timestamp = sgqlc.types.Field(LONG, graphql_name='endTimestamp')

    exception = sgqlc.types.Field(String, graphql_name='exception')

    docker_image_tag = sgqlc.types.Field(String, graphql_name='dockerImageTag')

    status = sgqlc.types.Field(sgqlc.types.non_null(JobStatus), graphql_name='status')



class DataParams(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('dataset_loader_name', 'dataset_loader_version', 'collector_name', 'dataset_loader_method_params', 'collector_method_params')
    dataset_loader_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='datasetLoaderName')

    dataset_loader_version = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='datasetLoaderVersion')

    collector_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='collectorName')

    dataset_loader_method_params = sgqlc.types.Field(sgqlc.types.non_null('MethodParams'), graphql_name='datasetLoaderMethodParams')

    collector_method_params = sgqlc.types.Field(sgqlc.types.non_null('MethodParams'), graphql_name='collectorMethodParams')



class DataSchema(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('dataset_loader_method_schema', 'collector_method_schema')
    dataset_loader_method_schema = sgqlc.types.Field(sgqlc.types.non_null('MethodSchema'), graphql_name='datasetLoaderMethodSchema')

    collector_method_schema = sgqlc.types.Field(sgqlc.types.non_null('MethodSchema'), graphql_name='collectorMethodSchema')



class DatasetLoader(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name', 'description', 'tags', 'creation_timestamp', 'last_updated_timestamp', 'owner', 'latest_dataset_loader_version', 'init_dataset_loader_version', 'list_dataset_loader_version', 'pagination_dataset_loader_version')
    name = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='name')

    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')

    tags = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='tags')

    creation_timestamp = sgqlc.types.Field(sgqlc.types.non_null(LONG), graphql_name='creationTimestamp')

    last_updated_timestamp = sgqlc.types.Field(LONG, graphql_name='lastUpdatedTimestamp')

    owner = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='owner')

    latest_dataset_loader_version = sgqlc.types.Field(sgqlc.types.non_null('DatasetLoaderVersion'), graphql_name='latestDatasetLoaderVersion')

    init_dataset_loader_version = sgqlc.types.Field(sgqlc.types.non_null('DatasetLoaderVersion'), graphql_name='initDatasetLoaderVersion')

    list_dataset_loader_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DatasetLoaderVersion'))), graphql_name='listDatasetLoaderVersion', args=sgqlc.types.ArgDict((
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    pagination_dataset_loader_version = sgqlc.types.Field(sgqlc.types.non_null('DatasetLoaderVersionPagination'), graphql_name='paginationDatasetLoaderVersion', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(ObjectVersionFilterSettings, graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `filter_settings` (`ObjectVersionFilterSettings`)None (default:
      `null`)
    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''



class DatasetLoaderPagination(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('list_dataset_loader', 'total')
    list_dataset_loader = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DatasetLoader))), graphql_name='listDatasetLoader')

    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')



class DatasetLoaderVersion(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name', 'version', 'source_path', 'tags', 'description', 'status', 'status_message', 'creation_timestamp', 'last_updated_timestamp', 'dataset_loader_method_schema', 'dataset_loader_method_schema_name', 'run', 'dataset_loader', 'data_json_schema', 'list_deployed_jobs', 'pagination_deployed_jobs')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    version = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='version')

    source_path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='sourcePath')

    tags = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='tags')

    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')

    status = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='status')

    status_message = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='statusMessage')

    creation_timestamp = sgqlc.types.Field(sgqlc.types.non_null(LONG), graphql_name='creationTimestamp')

    last_updated_timestamp = sgqlc.types.Field(LONG, graphql_name='lastUpdatedTimestamp')

    dataset_loader_method_schema = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='datasetLoaderMethodSchema')

    dataset_loader_method_schema_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='datasetLoaderMethodSchemaName')

    run = sgqlc.types.Field(sgqlc.types.non_null('Run'), graphql_name='run')

    dataset_loader = sgqlc.types.Field(sgqlc.types.non_null(DatasetLoader), graphql_name='datasetLoader')

    data_json_schema = sgqlc.types.Field(sgqlc.types.non_null(DataSchema), graphql_name='dataJsonSchema', args=sgqlc.types.ArgDict((
        ('collector_name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='collectorName', default=None)),
))
    )
    '''Arguments:

    * `collector_name` (`String!`)None
    '''

    list_deployed_jobs = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ExecutionJob'))), graphql_name='listDeployedJobs')

    pagination_deployed_jobs = sgqlc.types.Field(sgqlc.types.non_null('JobPagination'), graphql_name='paginationDeployedJobs', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    '''



class DatasetLoaderVersionPagination(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('list_dataset_loader_version', 'total')
    list_dataset_loader_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DatasetLoaderVersion))), graphql_name='listDatasetLoaderVersion')

    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')



class ExecutionJob(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name', 'periodic_type', 'status', 'registration_timestamp', 'start_timestamp', 'end_timestamp', 'exception', 'params', 'run', 'experiment', 'list_init_role_model_version', 'dataset_loader_version', 'executor_version', 'build_job', 'list_result_model_version', 'available_metrics', 'metric_history')
    name = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='name')

    periodic_type = sgqlc.types.Field(sgqlc.types.non_null(PeriodicType), graphql_name='periodicType')

    status = sgqlc.types.Field(sgqlc.types.non_null(JobStatus), graphql_name='status')

    registration_timestamp = sgqlc.types.Field(sgqlc.types.non_null(LONG), graphql_name='registrationTimestamp')

    start_timestamp = sgqlc.types.Field(LONG, graphql_name='startTimestamp')

    end_timestamp = sgqlc.types.Field(LONG, graphql_name='endTimestamp')

    exception = sgqlc.types.Field(String, graphql_name='exception')

    params = sgqlc.types.Field(sgqlc.types.non_null('JobParams'), graphql_name='params')

    run = sgqlc.types.Field('Run', graphql_name='run')

    experiment = sgqlc.types.Field('Experiment', graphql_name='experiment')

    list_init_role_model_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('RoleModelVersion'))), graphql_name='listInitRoleModelVersion')

    dataset_loader_version = sgqlc.types.Field(sgqlc.types.non_null(DatasetLoaderVersion), graphql_name='datasetLoaderVersion')

    executor_version = sgqlc.types.Field(sgqlc.types.non_null('ExecutorVersion'), graphql_name='executorVersion')

    build_job = sgqlc.types.Field(BuildJob, graphql_name='buildJob')

    list_result_model_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ModelVersion'))), graphql_name='listResultModelVersion', args=sgqlc.types.ArgDict((
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    available_metrics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='availableMetrics')

    metric_history = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Metric'))), graphql_name='metricHistory', args=sgqlc.types.ArgDict((
        ('metric', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='metric', default=None)),
))
    )
    '''Arguments:

    * `metric` (`String!`)None
    '''



class Executor(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name', 'description', 'tags', 'creation_timestamp', 'last_updated_timestamp', 'owner', 'latest_executor_version', 'init_executor_version', 'list_executor_version', 'pagination_executor_version')
    name = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='name')

    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')

    tags = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='tags')

    creation_timestamp = sgqlc.types.Field(sgqlc.types.non_null(LONG), graphql_name='creationTimestamp')

    last_updated_timestamp = sgqlc.types.Field(LONG, graphql_name='lastUpdatedTimestamp')

    owner = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='owner')

    latest_executor_version = sgqlc.types.Field(sgqlc.types.non_null('ExecutorVersion'), graphql_name='latestExecutorVersion')

    init_executor_version = sgqlc.types.Field(sgqlc.types.non_null('ExecutorVersion'), graphql_name='initExecutorVersion')

    list_executor_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ExecutorVersion'))), graphql_name='listExecutorVersion', args=sgqlc.types.ArgDict((
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    pagination_executor_version = sgqlc.types.Field(sgqlc.types.non_null('ExecutorVersionPagination'), graphql_name='paginationExecutorVersion', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(ObjectVersionFilterSettings, graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `filter_settings` (`ObjectVersionFilterSettings`)None (default:
      `null`)
    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''



class ExecutorPagination(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('list_executor', 'total')
    list_executor = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Executor))), graphql_name='listExecutor')

    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')



class ExecutorParams(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name', 'version', 'executor_method_params')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    version = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='version')

    executor_method_params = sgqlc.types.Field(sgqlc.types.non_null('MethodParams'), graphql_name='executorMethodParams')



class ExecutorVersion(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name', 'version', 'source_path', 'tags', 'description', 'status', 'status_message', 'creation_timestamp', 'last_updated_timestamp', 'executor_method_schema', 'executor_method_schema_name', 'desired_model_methods', 'upload_model_modes', 'desired_model_patterns', 'run', 'executor', 'list_deployed_jobs', 'pagination_deployed_jobs', 'job_json_schema', 'job_json_schema_for_role', 'available_models', 'pagination_available_models', 'available_model_versions', 'pagination_available_model_versions', 'available_dataset_loaders', 'pagination_available_dataset_loaders', 'available_dataset_loader_versions', 'pagination_available_dataset_loader_versions', 'available_collectors', 'pagination_available_collectors', 'build_job')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    version = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='version')

    source_path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='sourcePath')

    tags = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='tags')

    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')

    status = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='status')

    status_message = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='statusMessage')

    creation_timestamp = sgqlc.types.Field(sgqlc.types.non_null(LONG), graphql_name='creationTimestamp')

    last_updated_timestamp = sgqlc.types.Field(LONG, graphql_name='lastUpdatedTimestamp')

    executor_method_schema = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='executorMethodSchema')

    executor_method_schema_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='executorMethodSchemaName')

    desired_model_methods = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='desiredModelMethods')

    upload_model_modes = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='uploadModelModes')

    desired_model_patterns = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='desiredModelPatterns')

    run = sgqlc.types.Field(sgqlc.types.non_null('Run'), graphql_name='run')

    executor = sgqlc.types.Field(sgqlc.types.non_null(Executor), graphql_name='executor')

    list_deployed_jobs = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExecutionJob))), graphql_name='listDeployedJobs')

    pagination_deployed_jobs = sgqlc.types.Field(sgqlc.types.non_null('JobPagination'), graphql_name='paginationDeployedJobs', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    '''

    job_json_schema = sgqlc.types.Field(sgqlc.types.non_null('JobSchema'), graphql_name='jobJsonSchema', args=sgqlc.types.ArgDict((
        ('models', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RoleModelVersionInput))), graphql_name='models', default=None)),
))
    )
    '''Arguments:

    * `models` (`[RoleModelVersionInput!]!`)None
    '''

    job_json_schema_for_role = sgqlc.types.Field(sgqlc.types.non_null('RoleMethodSchema'), graphql_name='jobJsonSchemaForRole', args=sgqlc.types.ArgDict((
        ('model', sgqlc.types.Arg(sgqlc.types.non_null(RoleModelVersionInput), graphql_name='model', default=None)),
))
    )
    '''Arguments:

    * `model` (`RoleModelVersionInput!`)None
    '''

    available_models = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('InlineObject'))), graphql_name='availableModels', args=sgqlc.types.ArgDict((
        ('role', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='role', default=None)),
))
    )
    '''Arguments:

    * `role` (`String!`)None
    '''

    pagination_available_models = sgqlc.types.Field(sgqlc.types.non_null('InlineObjectPagination'), graphql_name='paginationAvailableModels', args=sgqlc.types.ArgDict((
        ('role', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='role', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('filter_settings', sgqlc.types.Arg(ObjectFilterSettings, graphql_name='filterSettings', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `role` (`String!`)None
    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `filter_settings` (`ObjectFilterSettings`)None (default: `null`)
    * `sorting` (`[ObjectSortBySortingInput!]`)None (default: `null`)
    '''

    available_model_versions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('InlineObjectVersion'))), graphql_name='availableModelVersions', args=sgqlc.types.ArgDict((
        ('role', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='role', default=None)),
        ('model_name', sgqlc.types.Arg(String, graphql_name='modelName', default=None)),
))
    )
    '''Arguments:

    * `role` (`String!`)None
    * `model_name` (`String`)None (default: `null`)
    '''

    pagination_available_model_versions = sgqlc.types.Field(sgqlc.types.non_null('InlineObjectVersionPagination'), graphql_name='paginationAvailableModelVersions', args=sgqlc.types.ArgDict((
        ('role', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='role', default=None)),
        ('model_name', sgqlc.types.Arg(String, graphql_name='modelName', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('filter_settings', sgqlc.types.Arg(ObjectVersionFilterSettings, graphql_name='filterSettings', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `role` (`String!`)None
    * `model_name` (`String`)None (default: `null`)
    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `filter_settings` (`ObjectVersionFilterSettings`)None (default:
      `null`)
    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    available_dataset_loaders = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('InlineObject'))), graphql_name='availableDatasetLoaders')

    pagination_available_dataset_loaders = sgqlc.types.Field(sgqlc.types.non_null('InlineObjectPagination'), graphql_name='paginationAvailableDatasetLoaders', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('filter_settings', sgqlc.types.Arg(ObjectFilterSettings, graphql_name='filterSettings', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `filter_settings` (`ObjectFilterSettings`)None (default: `null`)
    * `sorting` (`[ObjectSortBySortingInput!]`)None (default: `null`)
    '''

    available_dataset_loader_versions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('InlineObjectVersion'))), graphql_name='availableDatasetLoaderVersions', args=sgqlc.types.ArgDict((
        ('dataset_loader_name', sgqlc.types.Arg(String, graphql_name='datasetLoaderName', default=None)),
))
    )
    '''Arguments:

    * `dataset_loader_name` (`String`)None (default: `null`)
    '''

    pagination_available_dataset_loader_versions = sgqlc.types.Field(sgqlc.types.non_null('InlineObjectVersionPagination'), graphql_name='paginationAvailableDatasetLoaderVersions', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('dataset_loader_name', sgqlc.types.Arg(String, graphql_name='datasetLoaderName', default=None)),
        ('filter_settings', sgqlc.types.Arg(ObjectVersionFilterSettings, graphql_name='filterSettings', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `dataset_loader_name` (`String`)None (default: `null`)
    * `filter_settings` (`ObjectVersionFilterSettings`)None (default:
      `null`)
    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    available_collectors = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('InlineObject'))), graphql_name='availableCollectors')

    pagination_available_collectors = sgqlc.types.Field(sgqlc.types.non_null('InlineObjectPagination'), graphql_name='paginationAvailableCollectors', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('filter_settings', sgqlc.types.Arg(ObjectFilterSettings, graphql_name='filterSettings', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `filter_settings` (`ObjectFilterSettings`)None (default: `null`)
    '''

    build_job = sgqlc.types.Field(BuildJob, graphql_name='buildJob')



class ExecutorVersionPagination(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('list_executor_version', 'total')
    list_executor_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExecutorVersion))), graphql_name='listExecutorVersion')

    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')



class Experiment(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name', 'experiment_id', 'artifact_location', 'lifecycle_stage', 'list_run', 'pagination_run', 'tags', 'list_job', 'pagination_job', 'pagination_model', 'list_model', 'list_model_version', 'pagination_model_version')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    experiment_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='experimentId')

    artifact_location = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='artifactLocation')

    lifecycle_stage = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='lifecycleStage')

    list_run = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Run'))), graphql_name='listRun')

    pagination_run = sgqlc.types.Field(sgqlc.types.non_null('RunPagination'), graphql_name='paginationRun', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    '''

    tags = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='tags')

    list_job = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExecutionJob))), graphql_name='listJob')

    pagination_job = sgqlc.types.Field(sgqlc.types.non_null('JobPagination'), graphql_name='paginationJob', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('filter_settings', sgqlc.types.Arg(JobFilterSettings, graphql_name='filterSettings', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(JobsSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `filter_settings` (`JobFilterSettings`)None (default: `null`)
    * `sorting` (`[JobsSortBySortingInput!]`)None (default: `null`)
    '''

    pagination_model = sgqlc.types.Field(sgqlc.types.non_null('ModelPagination'), graphql_name='paginationModel', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(ObjectFilterSettings, graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `filter_settings` (`ObjectFilterSettings`)None (default: `null`)
    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `sorting` (`[ObjectSortBySortingInput!]`)None (default: `null`)
    '''

    list_model = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Model'))), graphql_name='listModel')

    list_model_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ModelVersion'))), graphql_name='listModelVersion', args=sgqlc.types.ArgDict((
        ('model_name', sgqlc.types.Arg(String, graphql_name='modelName', default=None)),
))
    )
    '''Arguments:

    * `model_name` (`String`)None (default: `null`)
    '''

    pagination_model_version = sgqlc.types.Field(sgqlc.types.non_null('ModelVersionPagination'), graphql_name='paginationModelVersion', args=sgqlc.types.ArgDict((
        ('model_name', sgqlc.types.Arg(String, graphql_name='modelName', default=None)),
        ('filter_settings', sgqlc.types.Arg(ObjectVersionFilterSettings, graphql_name='filterSettings', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
))
    )
    '''Arguments:

    * `model_name` (`String`)None (default: `null`)
    * `filter_settings` (`ObjectVersionFilterSettings`)None (default:
      `null`)
    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    '''



class ExperimentPagination(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('list_experiment', 'total')
    list_experiment = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Experiment))), graphql_name='listExperiment')

    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')



class GraphNode(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('run_id', 'name', 'version', 'source_run_id', 'source_name', 'source_version', 'root_run_id', 'upload_model_type', 'creation_timestamp', 'list_next_node')
    run_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='runId')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    version = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='version')

    source_run_id = sgqlc.types.Field(ID, graphql_name='sourceRunId')

    source_name = sgqlc.types.Field(String, graphql_name='sourceName')

    source_version = sgqlc.types.Field(String, graphql_name='sourceVersion')

    root_run_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='rootRunId')

    upload_model_type = sgqlc.types.Field(sgqlc.types.non_null(UploadModelType), graphql_name='uploadModelType')

    creation_timestamp = sgqlc.types.Field(sgqlc.types.non_null(LONG), graphql_name='creationTimestamp')

    list_next_node = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('GraphNode')), graphql_name='listNextNode', args=sgqlc.types.ArgDict((
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''



class InlineObject(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name',)
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')



class InlineObjectPagination(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('list_inline_object', 'total')
    list_inline_object = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(InlineObject))), graphql_name='listInlineObject')

    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')



class InlineObjectVersion(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name', 'version')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    version = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='version')



class InlineObjectVersionPagination(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('list_inline_object_version', 'total')
    list_inline_object_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(InlineObjectVersion))), graphql_name='listInlineObjectVersion')

    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')



class JobPagination(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('list_job', 'total')
    list_job = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExecutionJob))), graphql_name='listJob')

    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')



class JobParams(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name', 'experiment_name', 'cron_expression', 'periodic_type', 'executor_params', 'list_role_model_method_params', 'data_params')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    experiment_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='experimentName')

    cron_expression = sgqlc.types.Field(String, graphql_name='cronExpression')

    periodic_type = sgqlc.types.Field(sgqlc.types.non_null(PeriodicType), graphql_name='periodicType')

    executor_params = sgqlc.types.Field(sgqlc.types.non_null(ExecutorParams), graphql_name='executorParams')

    list_role_model_method_params = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('RoleModelMethodParams'))), graphql_name='listRoleModelMethodParams')

    data_params = sgqlc.types.Field(sgqlc.types.non_null(DataParams), graphql_name='dataParams')



class JobSchema(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('executor_method_schema', 'list_role_model_method_schemas')
    executor_method_schema = sgqlc.types.Field(sgqlc.types.non_null('MethodSchema'), graphql_name='executorMethodSchema')

    list_role_model_method_schemas = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('RoleMethodSchema'))), graphql_name='listRoleModelMethodSchemas')



class MethodParams(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('method_name', 'method_params')
    method_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='methodName')

    method_params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='methodParams')



class MethodSchema(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('schema_name', 'json_schema')
    schema_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='schemaName')

    json_schema = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='jsonSchema')



class Metric(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('key', 'value', 'step', 'timestamp')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')

    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='value')

    step = sgqlc.types.Field(Int, graphql_name='step')

    timestamp = sgqlc.types.Field(sgqlc.types.non_null(LONG), graphql_name='timestamp')



class Model(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name', 'description', 'tags', 'creation_timestamp', 'last_updated_timestamp', 'owner', 'latest_model_version', 'init_model_version', 'list_model_version', 'pagination_model_version', 'best_model_version')
    name = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='name')

    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')

    tags = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='tags')

    creation_timestamp = sgqlc.types.Field(sgqlc.types.non_null(LONG), graphql_name='creationTimestamp')

    last_updated_timestamp = sgqlc.types.Field(LONG, graphql_name='lastUpdatedTimestamp')

    owner = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='owner')

    latest_model_version = sgqlc.types.Field(sgqlc.types.non_null('ModelVersion'), graphql_name='latestModelVersion')

    init_model_version = sgqlc.types.Field(sgqlc.types.non_null('ModelVersion'), graphql_name='initModelVersion')

    list_model_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ModelVersion'))), graphql_name='listModelVersion', args=sgqlc.types.ArgDict((
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    pagination_model_version = sgqlc.types.Field(sgqlc.types.non_null('ModelVersionPagination'), graphql_name='paginationModelVersion', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(ObjectVersionFilterSettings, graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `filter_settings` (`ObjectVersionFilterSettings`)None (default:
      `null`)
    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    best_model_version = sgqlc.types.Field(sgqlc.types.non_null('ModelVersion'), graphql_name='bestModelVersion', args=sgqlc.types.ArgDict((
        ('metric', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='metric', default=None)),
        ('optimal_min', sgqlc.types.Arg(Boolean, graphql_name='optimalMin', default=False)),
))
    )
    '''Arguments:

    * `metric` (`String!`)None
    * `optimal_min` (`Boolean`)None (default: `false`)
    '''



class ModelPagination(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('list_model', 'total')
    list_model = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Model))), graphql_name='listModel')

    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')



class ModelVersion(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('name', 'version', 'source_path', 'tags', 'description', 'status', 'status_message', 'creation_timestamp', 'last_updated_timestamp', 'upload_model_type', 'model_method_schemas', 'list_deployed_jobs', 'pagination_deployed_jobs', 'list_eval_run', 'pagination_eval_run', 'run', 'group_job_run', 'group_job_run_id', 'source_run', 'root_run', 'model', 'available_executor_versions', 'pagination_available_executor_versions', 'available_executors', 'pagination_available_executors', 'available_dataset_loaders', 'pagination_available_dataset_loaders', 'available_dataset_loader_versions', 'pagination_available_dataset_loader_versions', 'available_collectors', 'pagination_available_collectors', 'list_next_graph_nodes', 'list_next_model_version', 'list_new_model_from_version', 'list_new_version_from_version', 'pagination_next_model_version', 'pagination_new_model_from_version', 'pagination_new_version_from_version', 'source_model_version', 'source_executor_version', 'root_model_version', 'list_lineage_model_version', 'pagination_lineage_model_version', 'build_job')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    version = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='version')

    source_path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='sourcePath')

    tags = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='tags')

    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')

    status = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='status')

    status_message = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='statusMessage')

    creation_timestamp = sgqlc.types.Field(sgqlc.types.non_null(LONG), graphql_name='creationTimestamp')

    last_updated_timestamp = sgqlc.types.Field(LONG, graphql_name='lastUpdatedTimestamp')

    upload_model_type = sgqlc.types.Field(sgqlc.types.non_null(UploadModelType), graphql_name='uploadModelType')

    model_method_schemas = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='modelMethodSchemas')

    list_deployed_jobs = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExecutionJob))), graphql_name='listDeployedJobs')

    pagination_deployed_jobs = sgqlc.types.Field(sgqlc.types.non_null(JobPagination), graphql_name='paginationDeployedJobs', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    '''

    list_eval_run = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Run'))), graphql_name='listEvalRun')

    pagination_eval_run = sgqlc.types.Field(sgqlc.types.non_null('RunPagination'), graphql_name='paginationEvalRun', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    '''

    run = sgqlc.types.Field(sgqlc.types.non_null('Run'), graphql_name='run')

    group_job_run = sgqlc.types.Field('Run', graphql_name='groupJobRun')

    group_job_run_id = sgqlc.types.Field(String, graphql_name='groupJobRunId')

    source_run = sgqlc.types.Field('Run', graphql_name='sourceRun')

    root_run = sgqlc.types.Field(sgqlc.types.non_null('Run'), graphql_name='rootRun')

    model = sgqlc.types.Field(sgqlc.types.non_null(Model), graphql_name='model')

    available_executor_versions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(InlineObjectVersion))), graphql_name='availableExecutorVersions', args=sgqlc.types.ArgDict((
        ('executor_name', sgqlc.types.Arg(String, graphql_name='executorName', default=None)),
))
    )
    '''Arguments:

    * `executor_name` (`String`)None (default: `null`)
    '''

    pagination_available_executor_versions = sgqlc.types.Field(sgqlc.types.non_null(InlineObjectVersionPagination), graphql_name='paginationAvailableExecutorVersions', args=sgqlc.types.ArgDict((
        ('executor_name', sgqlc.types.Arg(String, graphql_name='executorName', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('filter_settings', sgqlc.types.Arg(ObjectVersionFilterSettings, graphql_name='filterSettings', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `executor_name` (`String`)None (default: `null`)
    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `filter_settings` (`ObjectVersionFilterSettings`)None (default:
      `null`)
    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    available_executors = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(InlineObject))), graphql_name='availableExecutors')

    pagination_available_executors = sgqlc.types.Field(sgqlc.types.non_null(InlineObjectPagination), graphql_name='paginationAvailableExecutors', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('filter_settings', sgqlc.types.Arg(ObjectFilterSettings, graphql_name='filterSettings', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `filter_settings` (`ObjectFilterSettings`)None (default: `null`)
    * `sorting` (`[ObjectSortBySortingInput!]`)None (default: `null`)
    '''

    available_dataset_loaders = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(InlineObject))), graphql_name='availableDatasetLoaders')

    pagination_available_dataset_loaders = sgqlc.types.Field(sgqlc.types.non_null(InlineObjectPagination), graphql_name='paginationAvailableDatasetLoaders', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('filter_settings', sgqlc.types.Arg(ObjectFilterSettings, graphql_name='filterSettings', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `filter_settings` (`ObjectFilterSettings`)None (default: `null`)
    * `sorting` (`[ObjectSortBySortingInput!]`)None (default: `null`)
    '''

    available_dataset_loader_versions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(InlineObjectVersion))), graphql_name='availableDatasetLoaderVersions', args=sgqlc.types.ArgDict((
        ('dataset_loader_name', sgqlc.types.Arg(String, graphql_name='datasetLoaderName', default=None)),
))
    )
    '''Arguments:

    * `dataset_loader_name` (`String`)None (default: `null`)
    '''

    pagination_available_dataset_loader_versions = sgqlc.types.Field(sgqlc.types.non_null(InlineObjectVersionPagination), graphql_name='paginationAvailableDatasetLoaderVersions', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('dataset_loader_name', sgqlc.types.Arg(String, graphql_name='datasetLoaderName', default=None)),
        ('filter_settings', sgqlc.types.Arg(ObjectVersionFilterSettings, graphql_name='filterSettings', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `dataset_loader_name` (`String`)None (default: `null`)
    * `filter_settings` (`ObjectVersionFilterSettings`)None (default:
      `null`)
    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    available_collectors = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(InlineObject))), graphql_name='availableCollectors')

    pagination_available_collectors = sgqlc.types.Field(sgqlc.types.non_null(InlineObjectPagination), graphql_name='paginationAvailableCollectors', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('filter_settings', sgqlc.types.Arg(ObjectFilterSettings, graphql_name='filterSettings', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `filter_settings` (`ObjectFilterSettings`)None (default: `null`)
    '''

    list_next_graph_nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphNode))), graphql_name='listNextGraphNodes', args=sgqlc.types.ArgDict((
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    list_next_model_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ModelVersion'))), graphql_name='listNextModelVersion', args=sgqlc.types.ArgDict((
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    list_new_model_from_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ModelVersion'))), graphql_name='listNewModelFromVersion', args=sgqlc.types.ArgDict((
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    list_new_version_from_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ModelVersion'))), graphql_name='listNewVersionFromVersion', args=sgqlc.types.ArgDict((
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    pagination_next_model_version = sgqlc.types.Field(sgqlc.types.non_null('ModelVersionPagination'), graphql_name='paginationNextModelVersion', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    pagination_new_model_from_version = sgqlc.types.Field(sgqlc.types.non_null('ModelVersionPagination'), graphql_name='paginationNewModelFromVersion', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    pagination_new_version_from_version = sgqlc.types.Field(sgqlc.types.non_null('ModelVersionPagination'), graphql_name='paginationNewVersionFromVersion', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectVersionSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `sorting` (`[ObjectVersionSortBySortingInput!]`)None (default:
      `null`)
    '''

    source_model_version = sgqlc.types.Field('ModelVersion', graphql_name='sourceModelVersion')

    source_executor_version = sgqlc.types.Field(ExecutorVersion, graphql_name='sourceExecutorVersion')

    root_model_version = sgqlc.types.Field(sgqlc.types.non_null('ModelVersion'), graphql_name='rootModelVersion')

    list_lineage_model_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ModelVersion'))), graphql_name='listLineageModelVersion')

    pagination_lineage_model_version = sgqlc.types.Field(sgqlc.types.non_null('ModelVersionPagination'), graphql_name='paginationLineageModelVersion', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    '''

    build_job = sgqlc.types.Field(BuildJob, graphql_name='buildJob')



class ModelVersionPagination(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('list_model_version', 'total')
    list_model_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ModelVersion))), graphql_name='listModelVersion')

    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')



class Mutation(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('rename_experiment', 'add_ml_job', 'add_ml_job_single_model', 'delete_model', 'set_model_tag', 'delete_model_tag', 'set_model_description', 'delete_model_version_from_name_version', 'set_model_version_tag', 'delete_model_version_tag', 'set_model_version_description', 'rebuild_model_version_image', 'delete_dataset_loader', 'set_dataset_loader_tag', 'delete_dataset_loader_tag', 'set_dataset_loader_description', 'delete_dataset_loader_version_from_name_version', 'set_dataset_loader_version_tag', 'delete_dataset_loader_version_tag', 'set_dataset_loader_version_description', 'delete_executor', 'set_executor_tag', 'delete_executor_tag', 'set_executor_description', 'delete_executor_version_from_name_version', 'set_executor_version_tag', 'delete_executor_version_tag', 'set_executor_version_description', 'rebuild_no_model_executor_version_image')
    rename_experiment = sgqlc.types.Field(sgqlc.types.non_null(Experiment), graphql_name='renameExperiment', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
        ('new_name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='newName', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    * `new_name` (`String!`)None
    '''

    add_ml_job = sgqlc.types.Field(sgqlc.types.non_null(ExecutionJob), graphql_name='addMlJob', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(JobParameters), graphql_name='form', default=None)),
))
    )
    '''Arguments:

    * `form` (`JobParameters!`)None
    '''

    add_ml_job_single_model = sgqlc.types.Field(sgqlc.types.non_null(ExecutionJob), graphql_name='addMlJobSingleModel', args=sgqlc.types.ArgDict((
        ('form', sgqlc.types.Arg(sgqlc.types.non_null(JobSingleParameters), graphql_name='form', default=None)),
))
    )
    '''Arguments:

    * `form` (`JobSingleParameters!`)None
    '''

    delete_model = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleteModel', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    '''

    set_model_tag = sgqlc.types.Field(sgqlc.types.non_null(Model), graphql_name='setModelTag', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
        ('value', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='value', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    * `key` (`String!`)None
    * `value` (`String!`)None
    '''

    delete_model_tag = sgqlc.types.Field(sgqlc.types.non_null(Model), graphql_name='deleteModelTag', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    * `key` (`String!`)None
    '''

    set_model_description = sgqlc.types.Field(sgqlc.types.non_null(Model), graphql_name='setModelDescription', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
        ('description', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='description', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    * `description` (`String!`)None
    '''

    delete_model_version_from_name_version = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleteModelVersionFromNameVersion', args=sgqlc.types.ArgDict((
        ('model_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='modelVersion', default=None)),
))
    )
    '''Arguments:

    * `model_version` (`ObjectVersionInput!`)None
    '''

    set_model_version_tag = sgqlc.types.Field(sgqlc.types.non_null(ModelVersion), graphql_name='setModelVersionTag', args=sgqlc.types.ArgDict((
        ('model_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='modelVersion', default=None)),
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
        ('value', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='value', default=None)),
))
    )
    '''Arguments:

    * `model_version` (`ObjectVersionInput!`)None
    * `key` (`String!`)None
    * `value` (`String!`)None
    '''

    delete_model_version_tag = sgqlc.types.Field(sgqlc.types.non_null(ModelVersion), graphql_name='deleteModelVersionTag', args=sgqlc.types.ArgDict((
        ('model_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='modelVersion', default=None)),
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
))
    )
    '''Arguments:

    * `model_version` (`ObjectVersionInput!`)None
    * `key` (`String!`)None
    '''

    set_model_version_description = sgqlc.types.Field(sgqlc.types.non_null(ModelVersion), graphql_name='setModelVersionDescription', args=sgqlc.types.ArgDict((
        ('model_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='modelVersion', default=None)),
        ('description', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='description', default=None)),
))
    )
    '''Arguments:

    * `model_version` (`ObjectVersionInput!`)None
    * `description` (`String!`)None
    '''

    rebuild_model_version_image = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='rebuildModelVersionImage', args=sgqlc.types.ArgDict((
        ('model_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='modelVersion', default=None)),
))
    )
    '''Arguments:

    * `model_version` (`ObjectVersionInput!`)None
    '''

    delete_dataset_loader = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleteDatasetLoader', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    '''

    set_dataset_loader_tag = sgqlc.types.Field(sgqlc.types.non_null(DatasetLoader), graphql_name='setDatasetLoaderTag', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
        ('value', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='value', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    * `key` (`String!`)None
    * `value` (`String!`)None
    '''

    delete_dataset_loader_tag = sgqlc.types.Field(sgqlc.types.non_null(DatasetLoader), graphql_name='deleteDatasetLoaderTag', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    * `key` (`String!`)None
    '''

    set_dataset_loader_description = sgqlc.types.Field(sgqlc.types.non_null(DatasetLoader), graphql_name='setDatasetLoaderDescription', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
        ('description', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='description', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    * `description` (`String!`)None
    '''

    delete_dataset_loader_version_from_name_version = sgqlc.types.Field(Boolean, graphql_name='deleteDatasetLoaderVersionFromNameVersion', args=sgqlc.types.ArgDict((
        ('dataset_loader_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='datasetLoaderVersion', default=None)),
))
    )
    '''Arguments:

    * `dataset_loader_version` (`ObjectVersionInput!`)None
    '''

    set_dataset_loader_version_tag = sgqlc.types.Field(sgqlc.types.non_null(DatasetLoaderVersion), graphql_name='setDatasetLoaderVersionTag', args=sgqlc.types.ArgDict((
        ('dataset_loader_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='datasetLoaderVersion', default=None)),
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
        ('value', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='value', default=None)),
))
    )
    '''Arguments:

    * `dataset_loader_version` (`ObjectVersionInput!`)None
    * `key` (`String!`)None
    * `value` (`String!`)None
    '''

    delete_dataset_loader_version_tag = sgqlc.types.Field(sgqlc.types.non_null(DatasetLoaderVersion), graphql_name='deleteDatasetLoaderVersionTag', args=sgqlc.types.ArgDict((
        ('dataset_loader_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='datasetLoaderVersion', default=None)),
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
))
    )
    '''Arguments:

    * `dataset_loader_version` (`ObjectVersionInput!`)None
    * `key` (`String!`)None
    '''

    set_dataset_loader_version_description = sgqlc.types.Field(sgqlc.types.non_null(DatasetLoaderVersion), graphql_name='setDatasetLoaderVersionDescription', args=sgqlc.types.ArgDict((
        ('dataset_loader_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='datasetLoaderVersion', default=None)),
        ('description', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='description', default=None)),
))
    )
    '''Arguments:

    * `dataset_loader_version` (`ObjectVersionInput!`)None
    * `description` (`String!`)None
    '''

    delete_executor = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleteExecutor', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    '''

    set_executor_tag = sgqlc.types.Field(sgqlc.types.non_null(Executor), graphql_name='setExecutorTag', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
        ('value', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='value', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    * `key` (`String!`)None
    * `value` (`String!`)None
    '''

    delete_executor_tag = sgqlc.types.Field(sgqlc.types.non_null(Executor), graphql_name='deleteExecutorTag', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    * `key` (`String!`)None
    '''

    set_executor_description = sgqlc.types.Field(sgqlc.types.non_null(Executor), graphql_name='setExecutorDescription', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
        ('description', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='description', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    * `description` (`String!`)None
    '''

    delete_executor_version_from_name_version = sgqlc.types.Field(Boolean, graphql_name='deleteExecutorVersionFromNameVersion', args=sgqlc.types.ArgDict((
        ('executor_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='executorVersion', default=None)),
))
    )
    '''Arguments:

    * `executor_version` (`ObjectVersionInput!`)None
    '''

    set_executor_version_tag = sgqlc.types.Field(sgqlc.types.non_null(ExecutorVersion), graphql_name='setExecutorVersionTag', args=sgqlc.types.ArgDict((
        ('executor_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='executorVersion', default=None)),
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
        ('value', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='value', default=None)),
))
    )
    '''Arguments:

    * `executor_version` (`ObjectVersionInput!`)None
    * `key` (`String!`)None
    * `value` (`String!`)None
    '''

    delete_executor_version_tag = sgqlc.types.Field(sgqlc.types.non_null(ExecutorVersion), graphql_name='deleteExecutorVersionTag', args=sgqlc.types.ArgDict((
        ('executor_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='executorVersion', default=None)),
        ('key', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='key', default=None)),
))
    )
    '''Arguments:

    * `executor_version` (`ObjectVersionInput!`)None
    * `key` (`String!`)None
    '''

    set_executor_version_description = sgqlc.types.Field(sgqlc.types.non_null(ExecutorVersion), graphql_name='setExecutorVersionDescription', args=sgqlc.types.ArgDict((
        ('executor_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='executorVersion', default=None)),
        ('description', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='description', default=None)),
))
    )
    '''Arguments:

    * `executor_version` (`ObjectVersionInput!`)None
    * `description` (`String!`)None
    '''

    rebuild_no_model_executor_version_image = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='rebuildNoModelExecutorVersionImage', args=sgqlc.types.ArgDict((
        ('executor_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='executorVersion', default=None)),
))
    )
    '''Arguments:

    * `executor_version` (`ObjectVersionInput!`)None
    '''



class Query(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('graph_node', 'list_graph_node', 'list_subtree_graph_node', 'run_from_run_id', 'search_runs', 'list_experiment', 'pagination_experiment', 'experiment_from_name', 'experiment_from_id', 'job_from_name', 'list_job', 'pagination_job', 'model_from_name', 'warning_delete_model_query', 'list_model', 'pagination_model', 'model_version_from_run_id', 'model_version_from_name_version', 'list_initial_model_version', 'pagination_initial_model_version', 'list_dataset_loader', 'pagination_dataset_loader', 'dataset_loader_from_name', 'dataset_loader_version_from_name_version', 'dataset_loader_version_from_run_id', 'executor_from_name', 'list_executor', 'pagination_executor', 'executor_version_from_name_version', 'executor_version_from_run_id', 'list_initial_executor_version', 'pagination_initial_executor_version')
    graph_node = sgqlc.types.Field(sgqlc.types.non_null(GraphNode), graphql_name='graphNode', args=sgqlc.types.ArgDict((
        ('run_id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='runId', default=None)),
))
    )
    '''Arguments:

    * `run_id` (`String!`)None
    '''

    list_graph_node = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphNode))), graphql_name='listGraphNode')

    list_subtree_graph_node = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GraphNode))), graphql_name='listSubtreeGraphNode', args=sgqlc.types.ArgDict((
        ('root_run_id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='rootRunId', default=None)),
))
    )
    '''Arguments:

    * `root_run_id` (`String!`)None
    '''

    run_from_run_id = sgqlc.types.Field(sgqlc.types.non_null('Run'), graphql_name='runFromRunId', args=sgqlc.types.ArgDict((
        ('run_id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='runId', default=None)),
))
    )
    '''Arguments:

    * `run_id` (`String!`)None
    '''

    search_runs = sgqlc.types.Field(sgqlc.types.non_null('RunPagination'), graphql_name='searchRuns', args=sgqlc.types.ArgDict((
        ('experiment_ids', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='experimentIds', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('filter_string', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='filterString', default='')),
        ('run_view_type', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='runViewType', default=1)),
        ('order_by', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='orderBy', default=None)),
        ('experiment_names', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='experimentNames', default=None)),
))
    )
    '''Arguments:

    * `experiment_ids` (`[String!]`)None (default: `null`)
    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `filter_string` (`String!`)None (default: `""`)
    * `run_view_type` (`Int!`)None (default: `1`)
    * `order_by` (`[String!]`)None (default: `null`)
    * `experiment_names` (`[String!]`)None (default: `null`)
    '''

    list_experiment = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Experiment))), graphql_name='listExperiment')

    pagination_experiment = sgqlc.types.Field(sgqlc.types.non_null(ExperimentPagination), graphql_name='paginationExperiment', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    '''

    experiment_from_name = sgqlc.types.Field(sgqlc.types.non_null(Experiment), graphql_name='experimentFromName', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    '''

    experiment_from_id = sgqlc.types.Field(sgqlc.types.non_null(Experiment), graphql_name='experimentFromId', args=sgqlc.types.ArgDict((
        ('experiment_id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='experimentId', default=None)),
))
    )
    '''Arguments:

    * `experiment_id` (`String!`)None
    '''

    job_from_name = sgqlc.types.Field(sgqlc.types.non_null(ExecutionJob), graphql_name='jobFromName', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    '''

    list_job = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExecutionJob))), graphql_name='listJob')

    pagination_job = sgqlc.types.Field(sgqlc.types.non_null(JobPagination), graphql_name='paginationJob', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(JobsSortBySortingInput)), graphql_name='sorting', default=None)),
        ('filter_settings', sgqlc.types.Arg(JobFilterSettings, graphql_name='filterSettings', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `sorting` (`[JobsSortBySortingInput!]`)None (default: `null`)
    * `filter_settings` (`JobFilterSettings`)None (default: `null`)
    '''

    model_from_name = sgqlc.types.Field(sgqlc.types.non_null(Model), graphql_name='modelFromName', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    '''

    warning_delete_model_query = sgqlc.types.Field(sgqlc.types.non_null('WarningDeleteModel'), graphql_name='warningDeleteModelQuery', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    '''

    list_model = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Model))), graphql_name='listModel', args=sgqlc.types.ArgDict((
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `sorting` (`[ObjectSortBySortingInput!]`)None (default: `null`)
    '''

    pagination_model = sgqlc.types.Field(sgqlc.types.non_null(ModelPagination), graphql_name='paginationModel', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(ObjectFilterSettings, graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `filter_settings` (`ObjectFilterSettings`)None (default: `null`)
    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `sorting` (`[ObjectSortBySortingInput!]`)None (default: `null`)
    '''

    model_version_from_run_id = sgqlc.types.Field(sgqlc.types.non_null(ModelVersion), graphql_name='modelVersionFromRunId', args=sgqlc.types.ArgDict((
        ('run_id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='runId', default=None)),
))
    )
    '''Arguments:

    * `run_id` (`String!`)None
    '''

    model_version_from_name_version = sgqlc.types.Field(sgqlc.types.non_null(ModelVersion), graphql_name='modelVersionFromNameVersion', args=sgqlc.types.ArgDict((
        ('model_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='modelVersion', default=None)),
))
    )
    '''Arguments:

    * `model_version` (`ObjectVersionInput!`)None
    '''

    list_initial_model_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ModelVersion))), graphql_name='listInitialModelVersion')

    pagination_initial_model_version = sgqlc.types.Field(sgqlc.types.non_null(ModelVersionPagination), graphql_name='paginationInitialModelVersion', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    '''

    list_dataset_loader = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DatasetLoader))), graphql_name='listDatasetLoader', args=sgqlc.types.ArgDict((
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `sorting` (`[ObjectSortBySortingInput!]`)None (default: `null`)
    '''

    pagination_dataset_loader = sgqlc.types.Field(sgqlc.types.non_null(DatasetLoaderPagination), graphql_name='paginationDatasetLoader', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(ObjectFilterSettings, graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `filter_settings` (`ObjectFilterSettings`)None (default: `null`)
    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `sorting` (`[ObjectSortBySortingInput!]`)None (default: `null`)
    '''

    dataset_loader_from_name = sgqlc.types.Field(sgqlc.types.non_null(DatasetLoader), graphql_name='datasetLoaderFromName', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    '''

    dataset_loader_version_from_name_version = sgqlc.types.Field(sgqlc.types.non_null(DatasetLoaderVersion), graphql_name='datasetLoaderVersionFromNameVersion', args=sgqlc.types.ArgDict((
        ('dataset_loader_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='datasetLoaderVersion', default=None)),
))
    )
    '''Arguments:

    * `dataset_loader_version` (`ObjectVersionInput!`)None
    '''

    dataset_loader_version_from_run_id = sgqlc.types.Field(sgqlc.types.non_null(DatasetLoaderVersion), graphql_name='datasetLoaderVersionFromRunId', args=sgqlc.types.ArgDict((
        ('run_id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='runId', default=None)),
))
    )
    '''Arguments:

    * `run_id` (`String!`)None
    '''

    executor_from_name = sgqlc.types.Field(sgqlc.types.non_null(Executor), graphql_name='executorFromName', args=sgqlc.types.ArgDict((
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
))
    )
    '''Arguments:

    * `name` (`String!`)None
    '''

    list_executor = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Executor))), graphql_name='listExecutor', args=sgqlc.types.ArgDict((
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `sorting` (`[ObjectSortBySortingInput!]`)None (default: `null`)
    '''

    pagination_executor = sgqlc.types.Field(sgqlc.types.non_null(ExecutorPagination), graphql_name='paginationExecutor', args=sgqlc.types.ArgDict((
        ('filter_settings', sgqlc.types.Arg(ObjectFilterSettings, graphql_name='filterSettings', default=None)),
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ObjectSortBySortingInput)), graphql_name='sorting', default=None)),
))
    )
    '''Arguments:

    * `filter_settings` (`ObjectFilterSettings`)None (default: `null`)
    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    * `sorting` (`[ObjectSortBySortingInput!]`)None (default: `null`)
    '''

    executor_version_from_name_version = sgqlc.types.Field(sgqlc.types.non_null(ExecutorVersion), graphql_name='executorVersionFromNameVersion', args=sgqlc.types.ArgDict((
        ('executor_version', sgqlc.types.Arg(sgqlc.types.non_null(ObjectVersionInput), graphql_name='executorVersion', default=None)),
))
    )
    '''Arguments:

    * `executor_version` (`ObjectVersionInput!`)None
    '''

    executor_version_from_run_id = sgqlc.types.Field(sgqlc.types.non_null(ExecutorVersion), graphql_name='executorVersionFromRunId', args=sgqlc.types.ArgDict((
        ('run_id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='runId', default=None)),
))
    )
    '''Arguments:

    * `run_id` (`String!`)None
    '''

    list_initial_executor_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExecutorVersion))), graphql_name='listInitialExecutorVersion')

    pagination_initial_executor_version = sgqlc.types.Field(sgqlc.types.non_null(ExecutorVersionPagination), graphql_name='paginationInitialExecutorVersion', args=sgqlc.types.ArgDict((
        ('limit', sgqlc.types.Arg(Int, graphql_name='limit', default=None)),
        ('offset', sgqlc.types.Arg(Int, graphql_name='offset', default=None)),
))
    )
    '''Arguments:

    * `limit` (`Int`)None (default: `null`)
    * `offset` (`Int`)None (default: `null`)
    '''



class RoleMethodSchema(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('role', 'list_model_method_schemas')
    role = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='role')

    list_model_method_schemas = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MethodSchema))), graphql_name='listModelMethodSchemas')



class RoleModelMethodParams(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('role', 'name', 'version', 'params', 'choice_criteria', 'metric_name', 'optimal_min', 'new_model_name', 'description')
    role = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='role')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    version = sgqlc.types.Field(Int, graphql_name='version')

    params = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MethodParams))), graphql_name='params')

    choice_criteria = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='choiceCriteria')

    metric_name = sgqlc.types.Field(String, graphql_name='metricName')

    optimal_min = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='optimalMin')

    new_model_name = sgqlc.types.Field(String, graphql_name='newModelName')

    description = sgqlc.types.Field(String, graphql_name='description')



class RoleModelVersion(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('role', 'model_version')
    role = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='role')

    model_version = sgqlc.types.Field(sgqlc.types.non_null(ModelVersion), graphql_name='modelVersion')



class Run(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('run_id', 'artifact_uri', 'status', 'latest_metrics', 'experiment_id', 'params', 'start_time', 'end_time', 'lifecycle_stage', 'parent_job', 'list_artifacts', 'experiment', 'tags', 'metric_history')
    run_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='runId')

    artifact_uri = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='artifactUri')

    status = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='status')

    latest_metrics = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='latestMetrics')

    experiment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='experimentId')

    params = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='params')

    start_time = sgqlc.types.Field(sgqlc.types.non_null(LONG), graphql_name='startTime')

    end_time = sgqlc.types.Field(sgqlc.types.non_null(LONG), graphql_name='endTime')

    lifecycle_stage = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='lifecycleStage')

    parent_job = sgqlc.types.Field(ExecutionJob, graphql_name='parentJob')

    list_artifacts = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='listArtifacts')

    experiment = sgqlc.types.Field(sgqlc.types.non_null(Experiment), graphql_name='experiment')

    tags = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='tags')

    metric_history = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Metric))), graphql_name='metricHistory', args=sgqlc.types.ArgDict((
        ('metric', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='metric', default=None)),
))
    )
    '''Arguments:

    * `metric` (`String!`)None
    '''



class RunPagination(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('list_run', 'total')
    list_run = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Run))), graphql_name='listRun')

    total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='total')



class User(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')



class WarningDeleteModel(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('delete_possible', 'list_model_version')
    delete_possible = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deletePossible')

    list_model_version = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ModelVersion))), graphql_name='listModelVersion')




########################################################################
# Unions
########################################################################

########################################################################
# Schema Entry Points
########################################################################
schema.query_type = Query
schema.mutation_type = Mutation
schema.subscription_type = None

