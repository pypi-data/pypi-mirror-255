import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

# In pydantic v1, parse_raw_as was in the top level module
# In pydantic v2, parse_raw_as was moved to submodule v1
try:
    from pydantic.v1 import parse_raw_as
except ImportError:
    from pydantic import parse_raw_as  # type: ignore

from requests import Response
from tabulate import tabulate

from ml3_platform_sdk.core.connection import Connection
from ml3_platform_sdk.core.enums import (
    DataCategory,
    HTTPMethod,
    RawDataSourceType,
)
from ml3_platform_sdk.core.requests import (
    AddHistoricalRequest,
    AddKPIDataRequest,
    AddProductionRequest,
    AddReferenceRequest,
    AddRemoteHistoricalDataRequest,
    AddRemoteKPIDataRequest,
    AddRemoteModelReferenceRequest,
    AddRemoteProductionDataRequest,
    AddUserProjectRoleRequest,
    AzureSPCredentials,
    ChangeCompanyOwnerRequest,
    ChangeUserCompanyRoleRequest,
    ComputeRetrainingReportRequest,
    CreateApiKeyRequest,
    CreateAWSIntegrationCredentialsRequest,
    CreateAzureIntegrationCredentialsRequest,
    CreateCompanyRequest,
    CreateCompanyUserRequest,
    CreateDataSchemaRequest,
    CreateDetectionEventRuleRequest,
    CreateGCPIntegrationCredentialsRequest,
    CreateKPIRequest,
    CreateModelRequest,
    CreateProjectRequest,
    CreateTaskRequest,
    CreateUserApiRequest,
    DataSourceInfo,
    DeleteApiKeyRequest,
    DeleteCompanyUserRequest,
    DeleteUserApiKeyRequest,
    DeleteUserProjectRoleRequest,
    GCPAccountInfo,
    GetDataSchemaRequest,
    GetJobRequest,
    GetKPIRequest,
    GetKPIsRequest,
    GetModelRequest,
    GetModelsRequest,
    GetPresignedUrlRequest,
    GetRetrainingReportRequest,
    GetSuggestionsRequest,
    GetTaskRequest,
    GetTasksRequest,
    GetUserApiRequest,
    RetrainModelRequest,
    SetModelSuggestionTypeRequest,
    TestRetrainTriggerRequest,
    UpdateCompanyRequest,
    UpdateDetectionEventRuleRequest,
    UpdateModelVersionBySuggestionIDRequest,
    UpdateModelVersionFromRawDataRequest,
    UpdateModelVersionFromRemoteRawDataRequest,
    UpdateProjectRequest,
    UpdateTaskRequest,
)
from ml3_platform_sdk.core.responses import (
    GetPresignedUrlResponse,
    StandardErrorResponse,
)
from ml3_platform_sdk.enums import (
    ApiKeyExpirationTime,
    DatasetType,
    DetectionEventSeverity,
    DetectionEventType,
    ExternalIntegration,
    FileType,
    JobStatus,
    ModelMetricName,
    MonitoringTarget,
    StoragePolicy,
    StoringDataType,
    SuggestionType,
    TaskType,
    UserCompanyRole,
    UserProjectRole,
)
from ml3_platform_sdk.exceptions import (
    AddDataSchemaException,
    AddHistoricalDataException,
    AddKPIDataException,
    AddModelReferenceException,
    AddProductionDataException,
    ComputeRetrainingReportException,
    CreateCompanyException,
    CreateDetectionEventRuleException,
    CreateKPIException,
    CreateModelException,
    CreateProjectException,
    CreateTaskException,
    GetRetrainingReportException,
    InvalidActionList,
    JobFailureException,
    JobNotFoundException,
    JobWaitTimeoutException,
    SDKClientException,
    SetModelSuggestionTypeException,
    UpdateCompanyException,
    UpdateDetectionEventRuleException,
    UpdateModelVersionException,
    UpdateProjectException,
    UpdateTaskException,
)
from ml3_platform_sdk.models import (
    KPI,
    ApiKey,
    AWSCredentials,
    AzureBlobDataSource,
    AzureCredentials,
    Company,
    CompanyUser,
    DataSchema,
    DataSource,
    DetectionEventAction,
    DetectionEventRule,
    GCPCredentials,
    GCSDataSource,
    IntegrationCredentials,
    Job,
    LocalDataSource,
    Model,
    PredictionDataSourceInfo,
    Project,
    RemoteDataSource,
    RetrainAction,
    RetrainingReport,
    RetrainTrigger,
    S3DataSource,
    SecretAWSCredentials,
    SuggestionInfo,
    Task,
    TaskCostInfo,
)
from ml3_platform_sdk.utils import read_csv_file

STANDARD_TIMEOUT = 60

logger = logging.getLogger("ML3_PLATFORM_SDK")
logging.basicConfig(level=logging.INFO)

T = TypeVar('T', bound=SDKClientException)


class ML3PlatformClientImpl:
    """
    Client implementation for interacting with ML3Platform APIs
    """

    connection: Optional[Connection] = None
    allowed_remote_data_sources = [
        S3DataSource,
        GCSDataSource,
        AzureBlobDataSource,
    ]

    def __init__(self, url: str = '', api_key: str = ''):
        if len(url) > 0 and len(api_key) > 0:
            self.connection = Connection(url, api_key)
            logger.info("Client Initialized")

    def _api_call(
        self,
        method: HTTPMethod,
        path: str,
        json_payload: Optional[str] = None,
        params: Optional[dict] = None,
    ) -> Response:
        """
        Private method to make API calls
        """

        if self.connection is None or not self.connection.initialized:
            logger.info('***ERROR***')
            logger.info("Client NOT INITIALIZED check api_key and url")
            sys.exit(1)

        response = self.connection.send_api_request(
            method=method,
            path=path,
            timeout=STANDARD_TIMEOUT,
            params=params if method == HTTPMethod.GET else None,
            data=None if method == HTTPMethod.GET else json_payload,
        )

        # If the current task is running other operations
        # the api calls may return 503 error indicating
        # that at the moment the system is busy
        if response.status_code == 401:
            raise SDKClientException(
                error_code='UNAUTHORIZED', error_message='Unauthorized'
            )
        if int(response.status_code / 100) == 5:
            raise SDKClientException(
                error_code='INTERNAL_ERROR', error_message='Internal error'
            )

        return response

    @staticmethod
    def _validate_remote_source(
        data_source: RemoteDataSource,
        error_code: str,
        error_type: Type[SDKClientException],
    ) -> Tuple[str, RawDataSourceType]:
        """
        Validates that the remote data source is allowed, or it raises
        an exception.
        """

        if isinstance(data_source, S3DataSource):
            path = data_source.object_path

            if not path.lower().endswith('.csv'):
                raise error_type(
                    error_code=error_code,
                    error_message="Format not valid, currently only CSV "
                    "files are supported",
                )

            return path, RawDataSourceType.AWS_S3

        elif isinstance(data_source, GCSDataSource):
            path = data_source.object_path

            if not path.lower().endswith('.csv'):
                raise error_type(
                    error_code=error_code,
                    error_message="Format not valid, currently only CSV "
                    "files are supported",
                )

            return path, RawDataSourceType.GCS

        elif isinstance(data_source, AzureBlobDataSource):
            path = data_source.object_path

            if not path.lower().endswith('.csv'):
                raise error_type(
                    error_code=error_code,
                    error_message="Format not valid, currently only CSV "
                    "files are supported",
                )

            return path, RawDataSourceType.ABS

        raise NotImplementedError(
            f'Data source of type {type(data_source).__name__} '
            f'not implemented'
        )

    def _get_presigned_url_and_send_data(
        self,
        data_path: str,
        task_id: Optional[str],
        dataset_type: DatasetType,
        storing_data_type: StoringDataType,
        data_category: Optional[DataCategory],
        file_type: FileType = FileType.CSV,
        project_id: Optional[str] = None,
        model_id: Optional[str] = None,
        kpi_id: Optional[str] = None,
    ) -> GetPresignedUrlResponse:
        _, file_name = os.path.split(data_path)

        file_digest = read_csv_file(data_path)

        payload: GetPresignedUrlRequest = GetPresignedUrlRequest(
            project_id=project_id,
            task_id=task_id,
            dataset_type=dataset_type.value,
            storing_data_type=storing_data_type.value,
            file_name=file_name,
            file_type=file_type.value,
            file_checksum=file_digest,
            data_category=None
            if data_category is None
            else data_category.value,
            model_id=model_id,
            kpi_id=kpi_id,
        )

        get_presigned_url_response = self._get_presigned_url(payload.dict())

        self._send_data(
            data_path=data_path,
            get_presigned_url_response=get_presigned_url_response,
        )

        return get_presigned_url_response

    @staticmethod
    def _default_exception_handler(response, exception_type: Type[T]) -> None:
        if response.status_code == 400:
            response_model = parse_raw_as(
                StandardErrorResponse, response.content
            )

            ML3PlatformClientImpl._log_error(
                error_code=response_model.error_code,
                error_message=response_model.error_message,
            )

            raise exception_type(
                error_code=response_model.error_code,
                error_message=response_model.error_message,
            )
        raise SDKClientException()

    @staticmethod
    def _log_error(error_code: str, error_message: str):
        logger.error('%s - %s', error_code, error_message)

    @staticmethod
    def _print_table(items: List[Any], headers: List[str]):
        """
        Utility method to print
        """
        logger.info(
            "\n%s",
            tabulate(
                tabular_data=[list(dict(j).values()) for j in items],
                headers=headers,
            ),
        )

    def _get_presigned_url(self, payload: Dict) -> GetPresignedUrlResponse:
        get_presigned_url_raw_response = self._api_call(
            method=HTTPMethod.GET,
            path='/data/presigned-url',
            params=payload,
        )
        if get_presigned_url_raw_response.status_code != 200:
            self._default_exception_handler(
                get_presigned_url_raw_response, SDKClientException
            )
        return parse_raw_as(
            GetPresignedUrlResponse, get_presigned_url_raw_response.content
        )

    @classmethod
    def _send_data(
        cls,
        data_path: str,
        get_presigned_url_response: GetPresignedUrlResponse,
    ):
        send_data_raw_response = Connection.send_data(
            presigned_url=get_presigned_url_response.presigned_url,
            data_path=data_path,
        )
        if send_data_raw_response.status_code != 204:
            error_code = "SKD_CLIENT_UPLOAD_DATA_ERROR"
            error_message = "Error uploading data remotely"
            cls._log_error(error_code=error_code, error_message=error_message)
            raise SDKClientException(
                error_code=error_code, error_message=error_message
            )

    def create_company(self, name: str, address: str, vat: str) -> str:
        """
        create_company implementation
        """
        payload = CreateCompanyRequest(name=name, address=address, vat=vat)

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/company',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(response, CreateCompanyException)
        return response.json()

    def get_company(self) -> Company:
        """
        get_company implementation
        """

        response = self._api_call(
            method=HTTPMethod.GET,
            path='/company',
        )

        if response.status_code != 200:
            raise SDKClientException()

        return parse_raw_as(Company, response.content)

    def update_company(
        self, name: Optional[str], address: Optional[str], vat: Optional[str]
    ) -> None:
        """
        update_company implementation
        """
        payload = UpdateCompanyRequest(name=name, address=address, vat=vat)

        response = self._api_call(
            method=HTTPMethod.PATCH,
            path='/company',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(response, UpdateCompanyException)

    def create_project(
        self,
        name: str,
        description: Optional[str],
        default_storage_policy: StoragePolicy,
    ) -> str:
        """
        create_project implementation
        """
        payload = CreateProjectRequest(
            name=name,
            description=description,
            default_storage_policy=default_storage_policy,
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/project',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=CreateProjectException
            )
        return response.json()

    def get_projects(self) -> List[Project]:
        """
        get_projects implementation
        """
        response = self._api_call(
            method=HTTPMethod.GET,
            path='/projects',
        )

        if response.status_code == 200:
            return parse_raw_as(List[Project], response.content)
        raise SDKClientException()

    def get_project(self, project_id: str) -> Project:
        """
        get_project implementation
        """
        response = self._api_call(
            method=HTTPMethod.GET,
            path=f'/project/{project_id}',
        )

        if response.status_code == 200:
            return parse_raw_as(Project, response.content)
        raise SDKClientException()

    def update_project(
        self,
        project_id: str,
        name: Optional[str],
        description: Optional[str],
        default_storage_policy: Optional[StoragePolicy],
    ) -> None:
        """
        update_project implementation
        """
        payload = UpdateProjectRequest(
            project_id=project_id,
            name=name,
            description=description,
            default_storage_policy=default_storage_policy,
        )

        response = self._api_call(
            method=HTTPMethod.PATCH,
            path='/project',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(response, UpdateProjectException)

    def show_projects(self) -> None:
        """
        show_projects implementation
        """
        projects = self.get_projects()

        self._print_table(items=projects, headers=['Project Id', 'Name'])

    def create_task(
        self,
        project_id: str,
        name: str,
        tags: List[str],
        task_type: TaskType,
        cost_info: Optional[TaskCostInfo] = None,
        optional_target: bool = False,
    ) -> str:
        """
        create_task implementation
        """
        payload = CreateTaskRequest(
            project_id=project_id,
            name=name,
            tags=tags,
            task_type=task_type,
            cost_info=cost_info,
            optional_target=optional_target,
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/task',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=CreateTaskException
            )
        return response.json()

    def update_task(
        self,
        task_id: str,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        cost_info: Optional[TaskCostInfo] = None,
    ):
        """
        Update task attributes.
        """
        payload = UpdateTaskRequest(
            task_id=task_id,
            name=name,
            tags=tags,
            cost_info=cost_info,
        )

        response = self._api_call(
            method=HTTPMethod.PATCH,
            path='/task',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(response, UpdateTaskException)

    def get_tasks(self, project_id: str) -> List[Task]:
        """
        get_tasks implementation
        """
        payload = GetTasksRequest(project_id=project_id)

        response = self._api_call(
            method=HTTPMethod.GET, path=f'/tasks/{payload.project_id}'
        )

        if response.status_code == 200:
            return parse_raw_as(List[Task], response.content)
        raise SDKClientException()

    def get_task(self, task_id: str) -> Task:
        """
        get_task implementation
        """
        payload = GetTaskRequest(task_id=task_id)

        response = self._api_call(
            method=HTTPMethod.GET, path=f'/task/{payload.task_id}'
        )

        if response.status_code == 200:
            return parse_raw_as(Task, response.content)
        raise SDKClientException()

    def show_tasks(self, project_id: str):
        """
        show_tasks implementation
        """
        tasks = self.get_tasks(project_id)

        self._print_table(
            items=tasks,
            headers=['Task Id', 'Name', 'Type', 'Status', 'Status start date'],
        )

    def create_model(
        self,
        task_id: str,
        name: str,
        version: str,
        metric_name: ModelMetricName,
        preferred_suggestion_type: SuggestionType,
        retraining_cost: float = 0.0,
        resampled_dataset_size: Optional[int] = None,
    ) -> str:
        """
        create_model implementation
        """

        payload: CreateModelRequest = CreateModelRequest(
            task_id=task_id,
            name=name,
            version=version,
            metric_name=metric_name.value,
            retraining_cost=retraining_cost,
            preferred_suggestion_type=preferred_suggestion_type.value,
            resampled_dataset_size=resampled_dataset_size,
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/model',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=CreateModelException
            )
        return response.json()

    def set_model_suggestion_type(
        self,
        model_id: str,
        preferred_suggestion_type: SuggestionType,
        resampled_dataset_size: Optional[int] = None,
    ):
        """
        update_model_info implementation
        """

        payload: SetModelSuggestionTypeRequest = SetModelSuggestionTypeRequest(
            model_id=model_id,
            preferred_suggestion_type=preferred_suggestion_type.value,
            resampled_dataset_size=resampled_dataset_size,
        )

        response = self._api_call(
            method=HTTPMethod.PUT,
            path='/model/suggestion-type',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response,
                exception_type=SetModelSuggestionTypeException,
            )

    def get_models(self, task_id: str) -> List[Model]:
        """
        get_models implementation
        """
        payload = GetModelsRequest(task_id=task_id)

        response = self._api_call(
            method=HTTPMethod.GET, path=f'/models/{payload.task_id}'
        )

        if response.status_code == 200:
            return parse_raw_as(List[Model], response.content)
        raise SDKClientException()

    def get_model_by_name_and_version(
        self, task_id: str, model_name: str, model_version: str
    ) -> Model:
        """
        get_model_id implementation
        """

        models: List[Model] = self.get_models(task_id=task_id)

        for model in models:
            if model.name == model_name and model.version == model_version:
                return model

        raise SDKClientException(
            error_code="MODEL_NOT_FOUND",
            error_message=f"No model found with name: {model_name} and version: {model_version}",
        )

    def update_model_version_by_suggestion_id(
        self, model_id: str, new_model_version: str, suggestion_id: str
    ) -> str:
        """
        update_model_version_by_suggestion_id implementation
        """
        payload = UpdateModelVersionBySuggestionIDRequest(
            model_id=model_id,
            new_model_version=new_model_version,
            suggestion_id=suggestion_id,
        )

        response = self._api_call(
            method=HTTPMethod.PATCH,
            path='/model-version-suggestion-id',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=UpdateModelVersionException
            )
        return response.json()

    def update_model_version_from_raw_data(
        self,
        model_id: str,
        new_model_version: str,
        features_data_source: DataSource,
        targets_data_source: DataSource,
    ) -> str:
        """
        update_model_version_from_raw_data implementation
        """

        # For now, we support only homogeneous sources i.e., all local
        # or all remotes
        if isinstance(features_data_source, LocalDataSource) & isinstance(
            targets_data_source, LocalDataSource
        ):
            if (
                features_data_source.dataset_type
                != targets_data_source.dataset_type
            ):
                raise AttributeError(
                    "dataset types of the data sources must be the same"
                )
            return self._update_model_version_from_local_raw_data(
                model_id=model_id,
                new_model_version=new_model_version,
                dataset_type=features_data_source.dataset_type,
                features_data_path=features_data_source.file_path,  # type: ignore
                targets_data_path=targets_data_source.file_path,  # type: ignore
            )

        elif isinstance(features_data_source, RemoteDataSource) & isinstance(
            targets_data_source, RemoteDataSource
        ):
            return self._update_model_version_from_remote_raw_data(
                model_id=model_id,
                new_model_version=new_model_version,
                features_data_source=features_data_source,  # type: ignore
                targets_data_source=targets_data_source,  # type: ignore
            )

        raise NotImplementedError(
            f'Features data source of type '
            f'{type(features_data_source).__name__} '
            f'and targets data source of type'
            f'{type(targets_data_source).__name__} '
            f'are not implemented'
        )

    def _update_model_version_from_remote_raw_data(
        self,
        model_id: str,
        new_model_version: str,
        features_data_source: RemoteDataSource,
        targets_data_source: RemoteDataSource,
    ):
        """
        Update model version from remote raw data
        """
        (
            features_remote_path,
            features_ds_type,
        ) = ML3PlatformClientImpl._validate_remote_source(
            features_data_source,
            "UPDATE_MODEL_REFERENCE_FROM_RAW_DATA_MODEL_ERROR",
            UpdateModelVersionException,
        )
        (
            targets_remote_path,
            targets_ds_type,
        ) = ML3PlatformClientImpl._validate_remote_source(
            targets_data_source,
            "UPDATE_MODEL_REFERENCE_FROM_RAW_DATA_MODEL_ERROR",
            UpdateModelVersionException,
        )

        payload = UpdateModelVersionFromRemoteRawDataRequest(
            model_id=model_id,
            new_model_version=new_model_version,
            features_data_source_info=DataSourceInfo(
                dataset_type=features_data_source.dataset_type,
                file_type=FileType.CSV,
                data_source_type=features_ds_type,
                remote_path=features_remote_path,
                credentials_id=features_data_source.credentials_id,
                storage_policy=features_data_source.storage_policy,
            ),
            targets_data_source_info=DataSourceInfo(
                dataset_type=targets_data_source.dataset_type,
                file_type=FileType.CSV,
                data_source_type=targets_ds_type,
                remote_path=targets_remote_path,
                credentials_id=targets_data_source.credentials_id,
                storage_policy=targets_data_source.storage_policy,
            ),
        )

        response = self._api_call(
            method=HTTPMethod.PATCH,
            path='/model-version-raw-data/remote',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response, UpdateModelVersionException
            )
        return response.json()

    def _update_model_version_from_local_raw_data(
        self,
        model_id: str,
        new_model_version: str,
        dataset_type: DatasetType,
        features_data_path: str,
        targets_data_path: str,
    ) -> str:
        """
        Update model version from local raw data
        """

        if not targets_data_path.lower().endswith(
            '.csv'
        ) or not features_data_path.lower().endswith('.csv'):
            raise UpdateModelVersionException(
                error_code="UPDATE_MODEL_REFERENCE_FROM_RAW_DATA_FORMAT_ERROR",
                error_message="Format not valid, currently only CSV "
                "files are supported",
            )

        model = self.get_model(model_id=model_id)
        if model is None:
            raise UpdateModelVersionException(
                error_code="UPDATE_MODEL_REFERENCE_FROM_RAW_DATA_MODEL_ERROR",
                error_message="Model not found",
            )

        features_presigned_url_response: GetPresignedUrlResponse = (
            self._get_presigned_url_and_send_data(
                data_path=features_data_path,
                task_id=model.task_id,
                dataset_type=dataset_type,
                storing_data_type=StoringDataType.REFERENCE,
                data_category=DataCategory.FEATURES,
                model_id=model_id,
            )
        )

        target_presigned_url_response: GetPresignedUrlResponse = (
            self._get_presigned_url_and_send_data(
                data_path=features_data_path,
                task_id=model.task_id,
                dataset_type=dataset_type,
                storing_data_type=StoringDataType.REFERENCE,
                data_category=DataCategory.TARGET,
                model_id=model_id,
            )
        )

        payload = UpdateModelVersionFromRawDataRequest(
            model_id=model_id,
            new_model_version=new_model_version,
            features_raw_data_storing_process_id=features_presigned_url_response.storing_process_id,
            targets_raw_data_storing_process_id=target_presigned_url_response.storing_process_id,
        )

        response = self._api_call(
            method=HTTPMethod.PATCH,
            path='/model-version-raw-data',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response, UpdateModelVersionException
            )
        return response.json()

    def get_model(self, model_id: str) -> Model:
        """
        get_model implementation
        """
        payload = GetModelRequest(model_id=model_id)

        response = self._api_call(
            method=HTTPMethod.GET, path=f'/model/{payload.model_id}'
        )

        if response.status_code == 200:
            return parse_raw_as(Model, response.content)
        raise SDKClientException()

    def show_models(self, task_id: str) -> None:
        """
        show_models implementation
        """

        models = self.get_models(task_id=task_id)

        self._print_table(
            models,
            [
                'Model Id',
                'Task Id',
                'Name',
                'Version',
                'Status',
                'Status start timestamp',
                'Status insert date',
                'Metric Name',
            ],
        )

    def get_suggestions_info(
        self, model_id: str, model_version: str
    ) -> List[SuggestionInfo]:
        """
        get_suggestions_info implementation
        """
        payload = GetSuggestionsRequest(
            model_id=model_id, model_version=model_version
        )

        response = self._api_call(
            method=HTTPMethod.GET,
            path=f'/suggestions/{payload.model_id}/{payload.model_version}',
        )

        if response.status_code == 200:
            return parse_raw_as(List[SuggestionInfo], response.content)
        raise SDKClientException()

    def show_suggestions(self, model_id: str, model_version: str) -> None:
        """
        show_suggestions implementation
        """

        suggestions = self.get_suggestions_info(
            model_id=model_id, model_version=model_version
        )

        self._print_table(
            suggestions,
            [
                'SuggestionInfo Id',
                'Executed',
                'Timestamp',
            ],
        )

    # TODO controllare validazione DataSchema
    def add_data_schema(self, task_id: str, data_schema: DataSchema) -> None:
        """
        add_data_schema implementation
        """
        payload = CreateDataSchemaRequest(
            task_id=task_id, data_schema=data_schema
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/data-schema',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=AddDataSchemaException
            )

    def get_data_schema(self, task_id: str) -> DataSchema:
        """
        get_data_schema implementation
        """

        payload = GetDataSchemaRequest(task_id=task_id)

        response = self._api_call(
            method=HTTPMethod.GET,
            path=f'/data-schema/{payload.task_id}',
        )

        if response.status_code == 200:
            return parse_raw_as(DataSchema, response.content)
        raise SDKClientException()

    def show_data_schema(self, task_id: str):
        """
        show_data_schema implementation
        """

        data_schema = self.get_data_schema(task_id=task_id)
        self._print_table(
            [] if data_schema is None else data_schema.columns,
            headers=[
                'Column name',
                'Role',
                'Type',
                'Nullable',
                'Predicted Target',
                'Possible Values',
                'Model Id',
            ],
        )

    def add_historical_data(
        self,
        task_id: str,
        features_data_source: DataSource,
        targets_data_source: Optional[DataSource] = None,
    ) -> str:
        """
        add_historical_data implementation
        """

        # for now, we support only homogeneous dataset_type between
        # data sources
        if targets_data_source is not None:
            # we need to do double if because Python raises exception
            # TypeError: 'NoneType' object is not subscriptable
            if (
                features_data_source.dataset_type
                != targets_data_source.dataset_type
            ):
                raise AttributeError(
                    "dataset types of the data sources must be the same"
                )
        # For now, we support only homogeneous sources i.e., all local
        # or all remotes. Therefore, we use features_data_source to
        # decide the submethod to invoke, and then we check the
        # consistency of target_data_source if it is not None
        if isinstance(features_data_source, LocalDataSource):
            if targets_data_source is None:
                targets_data_path = None
            elif isinstance(targets_data_source, LocalDataSource):
                targets_data_path = targets_data_source.file_path
            else:
                raise NotImplementedError(
                    f'Features data source of type '
                    f'{type(features_data_source).__name__} '
                    f'and targets data source of type'
                    f'{type(targets_data_source).__name__} '
                    f'are not implemented'
                )

            return self._add_local_historical_data(
                task_id=task_id,
                dataset_type=features_data_source.dataset_type,
                features_data_path=features_data_source.file_path,  # type: ignore
                targets_data_path=targets_data_path,  # type: ignore
            )

        elif isinstance(features_data_source, RemoteDataSource):
            if (targets_data_source is not None) & ~isinstance(
                targets_data_source, RemoteDataSource
            ):
                raise NotImplementedError(
                    f'Features data source of type '
                    f'{type(features_data_source).__name__} '
                    f'and targets data source of type'
                    f'{type(targets_data_source).__name__} '
                    f'are not implemented'
                )

            return self._add_remote_historical_data(
                task_id=task_id,
                features_data_source=features_data_source,  # type: ignore
                targets_data_source=targets_data_source,  # type: ignore
            )
        else:
            raise NotImplementedError(
                f'Features data source of type '
                f'{type(features_data_source).__name__} '
                f'and targets data source of type'
                f'{type(targets_data_source).__name__} '
                f'are not implemented'
            )

    def _add_remote_historical_data(
        self,
        task_id: str,
        features_data_source: RemoteDataSource,
        targets_data_source: Optional[RemoteDataSource],
    ):
        """
        Add remote historical data
        """

        (
            features_remote_path,
            features_ds_type,
        ) = ML3PlatformClientImpl._validate_remote_source(
            features_data_source,
            "ADD_HISTORICAL_DATA_FORMAT_ERROR",
            AddHistoricalDataException,
        )

        if targets_data_source is not None:
            (
                targets_remote_path,
                targets_ds_type,
            ) = ML3PlatformClientImpl._validate_remote_source(
                targets_data_source,
                "ADD_HISTORICAL_DATA_FORMAT_ERROR",
                AddHistoricalDataException,
            )
            targets_data_source_info = DataSourceInfo(
                dataset_type=targets_data_source.dataset_type,
                file_type=FileType.CSV,
                data_source_type=targets_ds_type,
                remote_path=targets_remote_path,
                credentials_id=targets_data_source.credentials_id,
                storage_policy=targets_data_source.storage_policy,
            )
        else:
            targets_data_source_info = None

        payload = AddRemoteHistoricalDataRequest(
            task_id=task_id,
            features_data_source_info=DataSourceInfo(
                dataset_type=features_data_source.dataset_type,
                file_type=FileType.CSV,
                data_source_type=features_ds_type,
                remote_path=features_remote_path,
                credentials_id=features_data_source.credentials_id,
                storage_policy=features_data_source.storage_policy,
            ),
            targets_data_source_info=targets_data_source_info,
        )

        add_historical_data_response = self._api_call(
            method=HTTPMethod.POST,
            path='/data/historical/remote',
            json_payload=payload.json(),
        )

        if add_historical_data_response.status_code != 200:
            self._default_exception_handler(
                add_historical_data_response, AddHistoricalDataException
            )
        return add_historical_data_response.json()

    def _add_local_historical_data(
        self,
        task_id: str,
        dataset_type: DatasetType,
        features_data_path: str,
        targets_data_path: Optional[str],
    ):
        """
        Add local historical data
        """
        if not features_data_path.lower().endswith('.csv'):
            raise AddHistoricalDataException(
                error_code="ADD_HISTORICAL_DATA_FORMAT_ERROR",
                error_message="features_data_path has not valid format,"
                " currently only CSV files are supported",
            )
        if targets_data_path is not None:
            if not targets_data_path.lower().endswith('.csv'):
                raise AddHistoricalDataException(
                    error_code="ADD_HISTORICAL_DATA_FORMAT_ERROR",
                    error_message="targets_data_path has not valid format,"
                    " currently only CSV files are supported",
                )

        features_presigned_url_response: GetPresignedUrlResponse = (
            self._get_presigned_url_and_send_data(
                data_path=features_data_path,
                task_id=task_id,
                dataset_type=dataset_type,
                storing_data_type=StoringDataType.HISTORICAL,
                data_category=DataCategory.FEATURES,
                model_id=None,
            )
        )
        if targets_data_path is not None:
            target_presigned_url_response: GetPresignedUrlResponse = (
                self._get_presigned_url_and_send_data(
                    data_path=targets_data_path,
                    task_id=task_id,
                    dataset_type=dataset_type,
                    storing_data_type=StoringDataType.HISTORICAL,
                    data_category=DataCategory.TARGET,
                    model_id=None,
                )
            )
            targets_raw_data_storing_process_id = (
                target_presigned_url_response.storing_process_id
            )
        else:
            targets_raw_data_storing_process_id = None

        payload: AddHistoricalRequest = AddHistoricalRequest(
            task_id=task_id,
            features_raw_data_storing_process_id=features_presigned_url_response.storing_process_id,
            targets_raw_data_storing_process_id=targets_raw_data_storing_process_id,
        )

        add_historical_data_response = self._api_call(
            method=HTTPMethod.POST,
            path='/data/historical',
            json_payload=payload.json(),
        )

        if add_historical_data_response.status_code != 200:
            self._default_exception_handler(
                add_historical_data_response, AddHistoricalDataException
            )
        return add_historical_data_response.json()

    def add_model_reference(
        self,
        model_id: str,
        features_data_source: DataSource,
        targets_data_source: DataSource,
    ) -> str:
        """
        add_model_reference implementation
        """

        # For now, we support only homogeneous sources i.e., all local
        # or all remotes
        if isinstance(features_data_source, LocalDataSource) & isinstance(
            targets_data_source, LocalDataSource
        ):
            if (
                features_data_source.dataset_type
                != targets_data_source.dataset_type
            ):
                raise AttributeError(
                    "dataset types of the data sources must be the same"
                )
            return self._add_local_model_reference(
                model_id=model_id,
                dataset_type=features_data_source.dataset_type,
                features_data_path=features_data_source.file_path,  # type: ignore
                targets_data_path=targets_data_source.file_path,  # type: ignore
            )

        elif isinstance(features_data_source, RemoteDataSource) & isinstance(
            targets_data_source, RemoteDataSource
        ):
            return self._add_remote_model_reference(
                model_id=model_id,
                features_data_source=features_data_source,  # type: ignore
                targets_data_source=targets_data_source,  # type: ignore
            )

        raise NotImplementedError(
            f'Features data source of type '
            f'{type(features_data_source).__name__} '
            f'and targets data source of type'
            f'{type(targets_data_source).__name__} '
            f'are not implemented'
        )

    def _add_remote_model_reference(
        self,
        model_id: str,
        features_data_source: RemoteDataSource,
        targets_data_source: RemoteDataSource,
    ):
        """
        Add remote model reference
        """
        (
            features_remote_path,
            features_ds_type,
        ) = ML3PlatformClientImpl._validate_remote_source(
            features_data_source,
            "ADD_MODEL_REFERENCE_FORMAT_ERROR",
            AddModelReferenceException,
        )
        (
            targets_remote_path,
            targets_ds_type,
        ) = ML3PlatformClientImpl._validate_remote_source(
            targets_data_source,
            "ADD_MODEL_REFERENCE_FORMAT_ERROR",
            AddModelReferenceException,
        )

        payload = AddRemoteModelReferenceRequest(
            model_id=model_id,
            features_data_source_info=DataSourceInfo(
                dataset_type=features_data_source.dataset_type,
                file_type=FileType.CSV,
                data_source_type=features_ds_type,
                remote_path=features_remote_path,
                credentials_id=features_data_source.credentials_id,
                storage_policy=features_data_source.storage_policy,
            ),
            targets_data_source_info=DataSourceInfo(
                dataset_type=targets_data_source.dataset_type,
                file_type=FileType.CSV,
                data_source_type=targets_ds_type,
                remote_path=targets_remote_path,
                credentials_id=targets_data_source.credentials_id,
                storage_policy=targets_data_source.storage_policy,
            ),
        )

        add_model_reference_response = self._api_call(
            method=HTTPMethod.POST,
            path='/model/reference/remote',
            json_payload=payload.json(),
        )

        if add_model_reference_response.status_code != 200:
            self._default_exception_handler(
                add_model_reference_response, AddModelReferenceException
            )
        return add_model_reference_response.json()

    def _add_local_model_reference(
        self,
        model_id: str,
        dataset_type: DatasetType,
        features_data_path: str,
        targets_data_path: str,
    ):
        """
        Add local model reference
        """
        if not targets_data_path.lower().endswith(
            '.csv'
        ) or not features_data_path.lower().endswith('.csv'):
            raise AddModelReferenceException(
                error_code="ADD_MODEL_REFERENCE_FORMAT_ERROR",
                error_message="Format not valid, currently only CSV "
                "files are supported",
            )

        model = self.get_model(model_id=model_id)
        if model is None:
            raise AddModelReferenceException(
                error_code="ADD_MODEL_REFERENCE_MODEL_ERROR",
                error_message="Model not found",
            )

        features_presigned_url_response: GetPresignedUrlResponse = (
            self._get_presigned_url_and_send_data(
                data_path=features_data_path,
                task_id=model.task_id,
                dataset_type=dataset_type,
                storing_data_type=StoringDataType.REFERENCE,
                data_category=DataCategory.FEATURES,
                model_id=model_id,
            )
        )

        target_presigned_url_response: GetPresignedUrlResponse = (
            self._get_presigned_url_and_send_data(
                data_path=targets_data_path,
                task_id=model.task_id,
                dataset_type=dataset_type,
                storing_data_type=StoringDataType.REFERENCE,
                data_category=DataCategory.TARGET,
                model_id=model_id,
            )
        )

        payload = AddReferenceRequest(
            model_id=model_id,
            features_raw_data_storing_process_id=features_presigned_url_response.storing_process_id,
            targets_raw_data_storing_process_id=target_presigned_url_response.storing_process_id,
        )

        add_model_reference_response = self._api_call(
            method=HTTPMethod.POST,
            path='/model/reference',
            json_payload=payload.json(),
        )

        if add_model_reference_response.status_code != 200:
            self._default_exception_handler(
                add_model_reference_response, AddModelReferenceException
            )
        return add_model_reference_response.json()

    def add_production_data(
        self,
        task_id: str,
        features_data_source: Optional[DataSource] = None,
        targets_data_source: Optional[DataSource] = None,
        predictions_data_sources: Optional[
            List[PredictionDataSourceInfo]
        ] = None,
    ) -> str:
        """
        add_production_data implementation
        """
        if (
            (features_data_source is None)
            & (targets_data_source is None)
            & (predictions_data_sources is None)
        ):
            raise AddProductionDataException(
                error_code="ADD_PRODUCTION_DATA_NO_DATA_ERROR",
                error_message="No data provided",
            )

        if predictions_data_sources is None:
            models_predictions_data_sources_list: List[
                PredictionDataSourceInfo
            ] = []
        else:
            models_predictions_data_sources_list = predictions_data_sources
        # check at least one element is provided

        if (
            (
                (features_data_source is None)
                or isinstance(features_data_source, LocalDataSource)
            )
            & (
                (targets_data_source is None)
                or isinstance(targets_data_source, LocalDataSource)
            )
            & all(
                (
                    isinstance(
                        model_ds.predictions_data_source, LocalDataSource
                    )
                    for model_ds in models_predictions_data_sources_list
                )
            )
        ):
            if features_data_source is not None:
                dataset_type = features_data_source.dataset_type
            elif targets_data_source is not None:
                dataset_type = targets_data_source.dataset_type
            else:
                dataset_type = models_predictions_data_sources_list[
                    0
                ].predictions_data_source.dataset_type
            return self._add_local_production_data(
                task_id=task_id,
                dataset_type=dataset_type,
                features_data_path=features_data_source.file_path  # type: ignore
                if features_data_source is not None
                else None,
                targets_data_path=targets_data_source.file_path  # type: ignore
                if targets_data_source is not None
                else None,
                models_predictions_data_paths=[
                    (
                        model_ds.model_id,
                        model_ds.predictions_data_source.file_path,  # type: ignore
                    )
                    for model_ds in models_predictions_data_sources_list
                ],
            )

        if (
            (
                (features_data_source is None)
                or isinstance(features_data_source, RemoteDataSource)
            )
            & (
                (targets_data_source is None)
                or isinstance(targets_data_source, RemoteDataSource)
            )
            & all(
                (
                    isinstance(
                        model_ds.predictions_data_source, RemoteDataSource
                    )
                    for model_ds in models_predictions_data_sources_list
                )
            )
        ):
            return self._add_remote_production_data(
                task_id=task_id,
                features_data_source=features_data_source,  # type: ignore
                targets_data_source=targets_data_source,  # type: ignore
                models_predictions_data_sources=models_predictions_data_sources_list,
            )

        raise NotImplementedError(
            f'Features data source of type '
            f'{type(features_data_source).__name__} '
            f'and targets data source of type'
            f'{type(targets_data_source).__name__} '
            f'and model predictions data sources of type'
            f'{[type(model_ds).__name__ for model_ds in predictions_data_sources] if predictions_data_sources is not None else []} '
            f'are not implemented'
        )

    def _add_remote_production_data(
        self,
        task_id: str,
        features_data_source: Optional[RemoteDataSource],
        targets_data_source: Optional[RemoteDataSource],
        models_predictions_data_sources: List[PredictionDataSourceInfo],
    ):
        """
        Add remote production data
        """
        if features_data_source is not None:
            (
                features_remote_path,
                features_ds_type,
            ) = ML3PlatformClientImpl._validate_remote_source(
                features_data_source,
                "ADD_MODEL_PRODUCTION_FORMAT_ERROR",
                AddProductionDataException,
            )
            features_data_source_info = DataSourceInfo(
                dataset_type=features_data_source.dataset_type,
                file_type=FileType.CSV,
                data_source_type=features_ds_type,
                remote_path=features_remote_path,
                credentials_id=features_data_source.credentials_id,
                storage_policy=features_data_source.storage_policy,
            )
        else:
            features_data_source_info = None

        if targets_data_source is not None:
            (
                targets_remote_path,
                targets_ds_type,
            ) = ML3PlatformClientImpl._validate_remote_source(
                targets_data_source,
                "ADD_MODEL_PRODUCTION_FORMAT_ERROR",
                AddProductionDataException,
            )
            targets_data_source_info = DataSourceInfo(
                dataset_type=targets_data_source.dataset_type,
                file_type=FileType.CSV,
                data_source_type=targets_ds_type,
                remote_path=targets_remote_path,
                credentials_id=targets_data_source.credentials_id,
                storage_policy=targets_data_source.storage_policy,
            )
        else:
            targets_data_source_info = None

        predictions_data_source_info = []

        for model_ds in models_predictions_data_sources:
            # To avoid type problems
            assert isinstance(
                model_ds.predictions_data_source, RemoteDataSource
            )
            (
                model_remote_path,
                model_ds_type,
            ) = ML3PlatformClientImpl._validate_remote_source(
                model_ds.predictions_data_source,
                "ADD_MODEL_PRODUCTION_FORMAT_ERROR",
                AddProductionDataException,
            )
            predictions_data_source_info.append(
                (
                    model_ds.model_id,
                    DataSourceInfo(
                        dataset_type=model_ds.predictions_data_source.dataset_type,
                        file_type=FileType.CSV,
                        data_source_type=model_ds_type,
                        remote_path=model_remote_path,
                        credentials_id=model_ds.predictions_data_source.credentials_id,
                        storage_policy=model_ds.predictions_data_source.storage_policy,
                    ),
                )
            )

        payload = AddRemoteProductionDataRequest(
            task_id=task_id,
            features_data_source_info=features_data_source_info,
            targets_data_source_info=targets_data_source_info,
            predictions_data_source_info=predictions_data_source_info,
        )

        add_production_data_response = self._api_call(
            method=HTTPMethod.POST,
            path='/data/production/remote',
            json_payload=payload.json(),
        )

        if add_production_data_response.status_code != 200:
            self._default_exception_handler(
                add_production_data_response, AddProductionDataException
            )
        return add_production_data_response.json()

    def _add_local_production_data(
        self,
        task_id: str,
        dataset_type: DatasetType,
        features_data_path: Optional[str],
        targets_data_path: Optional[str],
        models_predictions_data_paths: Optional[List[Tuple[str, str]]],
    ):
        """
        Add local production data
        """
        if (
            features_data_path is None
            and targets_data_path is None
            and (
                models_predictions_data_paths is None
                or len(models_predictions_data_paths) == 0
            )
        ):
            raise AddProductionDataException(
                error_code="ADD_PRODUCTION_DATA_NO_DATA_ERROR",
                error_message="No data provided",
            )

        # check all models exist. Since we are already iterating,
        # we also check that all files are csv

        if (
            models_predictions_data_paths is not None
            and len(models_predictions_data_paths) > 0
        ):
            model_ids: List[str] = [
                model.model_id for model in self.get_models(task_id=task_id)
            ]

            for model_id, data_path in models_predictions_data_paths:
                if not data_path.lower().endswith('.csv'):
                    raise AddProductionDataException(
                        error_code="ADD_PRODUCTION_DATA_FORMAT_ERROR",
                        error_message="Format not valid, currently only CSV files are supported",
                    )

                if model_id not in model_ids:
                    raise AddProductionDataException(
                        error_code="ADD_PRODUCTION_DATA_MODEL_ERROR",
                        error_message=f"Model {model_id} not found",
                    )

        # check all files are csv. We also need to ensure that the str are
        # not None otherwise we can't call endswith

        if (
            features_data_path is not None
            and not features_data_path.lower().endswith('.csv')
        ):
            raise AddProductionDataException(
                error_code="ADD_PRODUCTION_DATA_FORMAT_ERROR",
                error_message="Format not valid, currently only CSV "
                "files are supported",
            )

        if (
            targets_data_path is not None
            and not targets_data_path.lower().endswith('.csv')
        ):
            raise AddProductionDataException(
                error_code="ADD_PRODUCTION_DATA_FORMAT_ERROR",
                error_message="Format not valid, currently only CSV files are supported",
            )

        # start operations

        features_raw_data_storing_process_id = None
        targets_raw_data_storing_process_id = None
        models_predictions_raw_data_storing_process_ids: List[str] = []

        if features_data_path is not None:
            features_presigned_url_response: GetPresignedUrlResponse = (
                self._get_presigned_url_and_send_data(
                    data_path=features_data_path,
                    task_id=task_id,
                    dataset_type=dataset_type,
                    storing_data_type=StoringDataType.PRODUCTION,
                    data_category=DataCategory.FEATURES,
                )
            )

            features_raw_data_storing_process_id = (
                features_presigned_url_response.storing_process_id
            )

        if targets_data_path is not None:
            target_presigned_url_response: GetPresignedUrlResponse = (
                self._get_presigned_url_and_send_data(
                    data_path=targets_data_path,
                    task_id=task_id,
                    dataset_type=dataset_type,
                    storing_data_type=StoringDataType.PRODUCTION,
                    data_category=DataCategory.TARGET,
                )
            )

            targets_raw_data_storing_process_id = (
                target_presigned_url_response.storing_process_id
            )

        if models_predictions_data_paths is not None:
            for model_id, data_path in models_predictions_data_paths:
                model_predictions_presigned_url_response: GetPresignedUrlResponse = self._get_presigned_url_and_send_data(
                    data_path=data_path,
                    task_id=task_id,
                    dataset_type=dataset_type,
                    storing_data_type=StoringDataType.PRODUCTION,
                    data_category=DataCategory.PREDICTION,
                    model_id=model_id,
                )

                models_predictions_raw_data_storing_process_ids.append(
                    model_predictions_presigned_url_response.storing_process_id
                )

        add_production_data_request = AddProductionRequest(
            task_id=task_id,
            features_raw_data_storing_process_id=features_raw_data_storing_process_id,
            targets_raw_data_storing_process_id=targets_raw_data_storing_process_id,
            predictions_raw_data_storing_process_ids=models_predictions_raw_data_storing_process_ids,
        )

        add_production_data_response = self._api_call(
            method=HTTPMethod.POST,
            path='/data/production',
            json_payload=add_production_data_request.json(),
        )

        if add_production_data_response.status_code != 200:
            self._default_exception_handler(
                add_production_data_response, AddProductionDataException
            )
        return add_production_data_response.json()

    def create_kpi(self, project_id: str, name: str) -> str:
        """
        create_kpi implementation
        """
        payload: CreateKPIRequest = CreateKPIRequest(
            project_id=project_id, name=name
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/kpi',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=CreateKPIException
            )
        return response.json()

    def get_kpi(self, kpi_id: str) -> KPI:
        """
        get_kpi implementation
        """
        payload = GetKPIRequest(kpi_id=kpi_id)

        response = self._api_call(
            method=HTTPMethod.GET, path=f'/kpi/{payload.kpi_id}'
        )

        if response.status_code == 200:
            return parse_raw_as(KPI, response.content)
        raise SDKClientException()

    def get_kpis(self, project_id: str) -> List[KPI]:
        """
        get_models implementation
        """
        payload = GetKPIsRequest(project_id=project_id)

        response = self._api_call(
            method=HTTPMethod.GET, path=f'/kpis/{payload.project_id}'
        )

        if response.status_code == 200:
            return parse_raw_as(List[KPI], response.content)
        raise SDKClientException()

    def show_kpis(self, project_id: str) -> None:
        """
        show_kpis implementation
        """

        kpis = self.get_kpis(project_id=project_id)

        self._print_table(
            kpis,
            [
                'KPI Id',
                'Name',
                'Status',
                'Status start timestamp',
                'Status insert date',
            ],
        )

    def add_kpi_data(
        self,
        project_id: str,
        kpi_id: str,
        kpi_data_source: DataSource,
    ) -> str:
        """
        add_kpi_data implementation
        """

        if isinstance(kpi_data_source, LocalDataSource):
            return self._add_local_kpi_data(
                project_id=project_id,
                kpi_id=kpi_id,
                kpi_data_path=kpi_data_source.file_path,  # type: ignore
            )

        elif isinstance(kpi_data_source, RemoteDataSource):
            return self._add_remote_kpi_data(
                kpi_id=kpi_id,
                kpi_data_source=kpi_data_source,  # type: ignore
            )

        raise NotImplementedError(
            f'Data source of type '
            f'{type(kpi_data_source).__name__} '
            f'is not implemented'
        )

    def _add_local_kpi_data(
        self,
        project_id: str,
        kpi_id: str,
        kpi_data_path: str,
    ):
        """
        Add local kpi
        """
        if not kpi_data_path.lower().endswith('.csv'):
            raise AddKPIDataException(
                error_code="ADD_KPI_DATA_FORMAT_ERROR",
                error_message="Format not valid, currently only CSV "
                "files are supported",
            )

        kpi = self.get_kpi(kpi_id=kpi_id)
        if kpi is None:
            raise AddKPIDataException(
                error_code="ADD_KPI_DATA_ERROR",
                error_message="KPI not found",
            )

        kpi_presigned_url_response: GetPresignedUrlResponse = (
            self._get_presigned_url_and_send_data(
                project_id=project_id,
                task_id=None,
                data_path=kpi_data_path,
                storing_data_type=StoringDataType.KPI,
                data_category=None,
                dataset_type=DatasetType.TABULAR,
                kpi_id=kpi_id,
            )
        )

        payload = AddKPIDataRequest(
            kpi_id=kpi_id,
            kpi_raw_data_storing_process_id=kpi_presigned_url_response.storing_process_id,
        )

        add_kpi_data_response = self._api_call(
            method=HTTPMethod.POST,
            path='/data/kpi',
            json_payload=payload.json(),
        )

        if add_kpi_data_response.status_code != 200:
            self._default_exception_handler(
                add_kpi_data_response, AddKPIDataException
            )
        return add_kpi_data_response.json()

    def _add_remote_kpi_data(
        self,
        kpi_id: str,
        kpi_data_source: RemoteDataSource,
    ):
        """
        Add remote kpi data
        """

        (
            kpi_remote_path,
            kpi_ds_type,
        ) = ML3PlatformClientImpl._validate_remote_source(
            kpi_data_source, "ADD_KPI_DATA_FORMAT_ERROR", AddKPIDataException
        )

        payload = AddRemoteKPIDataRequest(
            kpi_id=kpi_id,
            kpi_data_source_info=DataSourceInfo(
                dataset_type=kpi_data_source.dataset_type,
                file_type=FileType.CSV,
                data_source_type=kpi_ds_type,
                remote_path=kpi_remote_path,
                credentials_id=kpi_data_source.credentials_id,
                storage_policy=kpi_data_source.storage_policy,
            ),
        )

        add_kpi_data_response = self._api_call(
            method=HTTPMethod.POST,
            path='/data/kpi/remote',
            json_payload=payload.json(),
        )

        if add_kpi_data_response.status_code != 200:
            self._default_exception_handler(
                add_kpi_data_response, AddKPIDataException
            )
        return add_kpi_data_response.json()

    def compute_retraining_report(
        self,
        model_id: str,
    ) -> str:
        """
        compute_retraining_report implementation
        """

        payload = ComputeRetrainingReportRequest(model_id=model_id)

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/retraining-report',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response, ComputeRetrainingReportException
            )
        return response.json()

    # TODO ricontrollare modelli
    def get_retraining_report(self, model_id: str) -> RetrainingReport:
        """
        get_retraining_report implementation
        """

        payload = GetRetrainingReportRequest(
            model_id=model_id,
        )

        response = self._api_call(
            method=HTTPMethod.GET,
            path='/retraining-report',
            params=payload.dict(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response, GetRetrainingReportException
            )

        return parse_raw_as(RetrainingReport, response.content)

    def get_jobs(
        self,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        model_id: Optional[str] = None,
        status: Optional[JobStatus] = None,
        job_id: Optional[str] = None,
    ) -> List[Job]:
        """
        get_jobs implementation
        """
        payload = GetJobRequest(
            project_id=project_id,
            task_id=task_id,
            model_id=model_id,
            status=status.value if status is not None else None,
            job_id=job_id,
        )

        response = self._api_call(
            method=HTTPMethod.GET,
            path='/job',
            params=payload.dict(),
        )

        if response.status_code != 200:
            self._default_exception_handler(response, SDKClientException)

        return parse_raw_as(List[Job], response.content)

    def get_job(self, job_id: str) -> Job:
        """
        get_job implementation
        """
        jobs: List[Job] = self.get_jobs(job_id=job_id)
        if len(jobs) == 1:
            return jobs[0]
        raise SDKClientException(f'got more than one job for id {job_id}')

    def show_jobs(
        self,
    ) -> None:
        """
        show_jobs implementation
        """

        jobs: List[Job] = self.get_jobs()

        self._print_table(
            items=jobs,
            headers=[
                'Job Id',
                'Job Type',
                'Project Id',
                'Project Name',
                'Task Id',
                'Task Name',
                'Model Id',
                'Model Name',
                'Status',
                'Error',
            ],
        )

    def get_detection_event_rules(
        self, task_id: str
    ) -> List[DetectionEventRule]:
        """
        get_detection_event_rules implementation
        """

        response = self._api_call(
            method=HTTPMethod.GET,
            path='/task/detection-event/rules',
            params={'task_id': task_id},
        )

        if response.status_code != 200:
            self._default_exception_handler(response, SDKClientException)

        return parse_raw_as(List[DetectionEventRule], response.content)

    def get_detection_event_rule(self, rule_id: str) -> DetectionEventRule:
        """
        get_detection_event_rule implementation
        """

        response = self._api_call(
            method=HTTPMethod.GET,
            path=f'/task/detection-event/rule/{rule_id}',
        )

        if response.status_code != 200:
            self._default_exception_handler(response, SDKClientException)

        return parse_raw_as(DetectionEventRule, response.content)

    @staticmethod
    def _validate_rule_actions(
        actions: List[DetectionEventAction],
        model_name: Optional[str],
    ) -> List[DetectionEventAction]:
        """
        Action check: if there is RetrainAction it should be valid
        that means:
          1- model_name of the rule is not None
          2- model_name of the action is None or equal to model_name
              of the rule
          3- there is only one retrain action
        """
        retrain_actions = list(
            filter(lambda x: isinstance(x, RetrainAction), actions)
        )
        n_retrain_actions = len(retrain_actions)
        # Only one retrain action is allowed
        if n_retrain_actions > 1:
            raise InvalidActionList(
                f'There are {n_retrain_actions} RetrainAction objects '
                f'but the maximum allowed number is 1'
            )

        if n_retrain_actions > 0:
            # the rule target must be the model
            if model_name is None:
                raise InvalidActionList(
                    'There is a RetrainAction but model_name is missing'
                )
            # if the RetrainAction does not have the model_name we set
            # it equal to the target.
            retrain_action = retrain_actions[0]
            assert isinstance(retrain_action, RetrainAction)
            if retrain_action.model_name is None:
                retrain_action.model_name = model_name
            else:
                # if the model_name is present, then it must be equal
                # to the target
                if retrain_action.model_name != model_name:
                    raise InvalidActionList(
                        f"RetrainAction must have the same model_name as "
                        f"rule target. RetrainAction.model_name = "
                        f"{retrain_action.model_name}"
                        f"model_name ? {model_name}"
                    )
        return actions

    def create_detection_event_rule(
        self,
        name: str,
        task_id: str,
        severity: DetectionEventSeverity,
        detection_event_type: DetectionEventType,
        monitoring_target: MonitoringTarget,
        actions: List[DetectionEventAction],
        model_name: Optional[str] = None,
    ) -> str:
        """
        create_detection_event_rule implementation
        """
        try:
            actions = self._validate_rule_actions(
                actions=actions, model_name=model_name
            )
        except InvalidActionList as e:
            raise CreateDetectionEventRuleException(
                error_code='CREATE_DETECTION_EVENT_RULE_ERROR',
                error_message='Failed rule action validation',
            ) from e

        payload = CreateDetectionEventRuleRequest(
            name=name,
            task_id=task_id,
            model_name=model_name,
            severity=severity,
            detection_event_type=detection_event_type,
            monitoring_target=monitoring_target,
            actions=[a.dict() for a in actions],
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/task/detection-event/rule',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response,
                exception_type=CreateDetectionEventRuleException,
            )
        return response.json()

    def update_detection_event_rule(
        self,
        rule_id: str,
        name: Optional[str] = None,
        model_name: Optional[str] = None,
        severity: Optional[DetectionEventSeverity] = None,
        detection_event_type: Optional[DetectionEventType] = None,
        monitoring_target: Optional[MonitoringTarget] = None,
        actions: Optional[List[DetectionEventAction]] = None,
    ):
        """
        update_detection_event_rule implementation
        """
        if actions is not None:
            try:
                actions = self._validate_rule_actions(
                    actions=actions, model_name=model_name
                )
            except InvalidActionList as e:
                raise UpdateDetectionEventRuleException(
                    error_code='UPDATE_DETECTION_EVENT_RULE_ERROR',
                    error_message='Failed rule action validation',
                ) from e
        payload = UpdateDetectionEventRuleRequest(
            rule_id=rule_id,
            name=name,
            model_name=model_name,
            severity=severity,
            detection_event_type=detection_event_type,
            monitoring_target=monitoring_target,
            actions=None if actions is None else [a.dict() for a in actions],
        )

        response = self._api_call(
            method=HTTPMethod.PATCH,
            path='/task/detection-event/rule',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response,
                exception_type=UpdateDetectionEventRuleException,
            )
        return response.json()

    def delete_detection_event_rule(self, rule_id: str):
        """
        delete_detection_event_rule implementation
        """

        response = self._api_call(
            method=HTTPMethod.DELETE,
            path=f'/task/detection-event/rule/{rule_id}',
        )

        if response.status_code != 200:
            self._default_exception_handler(response, SDKClientException)

    def wait_job_completion(self, job_id: str, max_wait_timeout: int = 900):
        """
        Utility function to wait for job completion
        """

        completed = False
        start_timestamp = int(time.time())

        while not completed:
            current_timestamp = int(time.time())
            if current_timestamp - start_timestamp > max_wait_timeout:
                raise JobWaitTimeoutException()

            job = self.get_job(job_id=job_id)
            if job is None:
                raise JobNotFoundException()

            if job.status == JobStatus.ERROR.value:
                raise JobFailureException()

            completed = job.status == JobStatus.COMPLETED.value

            time.sleep(int(os.environ.get('MLCUBE_POLLING', '30')))

    def create_company_user(
        self,
        name: str,
        surname: str,
        username: str,
        password: str,
        email: str,
        company_role: UserCompanyRole,
    ) -> str:
        """
        create_company_user implementation
        """
        payload = CreateCompanyUserRequest(
            name=name,
            surname=surname,
            username=username,
            email=email,
            password=password,
            company_role=company_role,
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/company-user',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )
        return response.json()

    def get_company_users(self) -> List[CompanyUser]:
        """
        get_company_users implementation
        """

        response = self._api_call(
            method=HTTPMethod.GET,
            path='/company-user',
        )

        if response.status_code != 200:
            self._default_exception_handler(response, SDKClientException)

        return parse_raw_as(List[CompanyUser], response.content)

    def change_user_company_role(
        self, user_id: str, company_role: UserCompanyRole
    ):
        """
        change_company_role implementation
        """
        request = ChangeUserCompanyRoleRequest(
            user_id=user_id, company_role=company_role
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/change-user-company-role',
            json_payload=request.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

    def show_company_users(self):
        """
        show_company_users implementation
        """

        items = self.get_company_users()

        self._print_table(
            items,
            ['User Id', 'Company Role'],
        )

    def get_user_projects(self, user_id: str) -> List[Project]:
        """
        get_user_projects implementation
        """
        response = self._api_call(
            method=HTTPMethod.GET,
            path=f'/user-project/{user_id}',
        )

        if response.status_code != 200:
            self._default_exception_handler(response, SDKClientException)

        return parse_raw_as(List[Project], response.content)

    def show_user_projects(self, user_id: str):
        """
        show_user_projects implementation
        """

        items = self.get_user_projects(user_id=user_id)

        self._print_table(
            items,
            ['Project Id', 'Name'],
        )

    def add_user_project_role(
        self, user_id: str, project_id: str, project_role: UserProjectRole
    ):
        """
        add_project_role implementation
        """
        request = AddUserProjectRoleRequest(
            user_id=user_id, project_id=project_id, project_role=project_role
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/user-project-role',
            json_payload=request.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

    def delete_project_role(self, user_id: str, project_id: str):
        """
        delete_project_role implementation
        """
        request = DeleteUserProjectRoleRequest(
            user_id=user_id, project_id=project_id
        )

        response = self._api_call(
            method=HTTPMethod.DELETE,
            path='/user-project-role',
            json_payload=request.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

    def get_api_keys(self) -> List[ApiKey]:
        """
        get_api_keys implementation
        """

        response = self._api_call(
            method=HTTPMethod.GET,
            path='/api-key',
        )

        if response.status_code != 200:
            self._default_exception_handler(response, SDKClientException)

        return parse_raw_as(List[ApiKey], response.content)

    def show_api_keys(self):
        """
        show_api_keys implementation
        """

        items = self.get_api_keys()

        self._print_table(
            items,
            ['Api Key', 'Name', 'Expiration Time'],
        )

    def create_api_key(
        self, name: str, expiration_time: ApiKeyExpirationTime
    ) -> str:
        """
        create_api_key implementation
        """

        request = CreateApiKeyRequest(
            name=name,
            expiration_time=expiration_time,
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/api-key',
            json_payload=request.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

        return response.json()

    def delete_api_key(self, api_key: str):
        """
        delete_api_key implementation
        """

        request = DeleteApiKeyRequest(api_key=api_key)

        response = self._api_call(
            method=HTTPMethod.DELETE, path=f'/api-key/{request.api_key}'
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

    def show_user_api_keys(self, user_id: str):
        """
        show_user_api_keys implementation
        """
        items = self.get_user_api_keys(user_id=user_id)

        self._print_table(
            items,
            ['Api Key', 'Name', 'Expiration Time'],
        )

    def get_user_api_keys(self, user_id: str) -> List[ApiKey]:
        """
        get_user_api_keys implementation
        """

        request = GetUserApiRequest(user_id=user_id)

        response = self._api_call(
            method=HTTPMethod.GET,
            path=f'/user-api-key/{request.user_id}',
        )

        if response.status_code != 200:
            self._default_exception_handler(response, SDKClientException)

        return parse_raw_as(List[ApiKey], response.content)

    def create_user_api_key(
        self, user_id: str, name: str, expiration_time: ApiKeyExpirationTime
    ) -> str:
        """
        create_user_api_key implementation
        """

        request = CreateUserApiRequest(
            user_id=user_id, name=name, expiration_time=expiration_time
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/user-api-key',
            json_payload=request.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )
        return response.json()

    def delete_user_api_key(self, user_id: str, api_key: str):
        """
        delete_user_api_key implementation
        """
        request = DeleteUserApiKeyRequest(user_id=user_id, api_key=api_key)

        response = self._api_call(
            method=HTTPMethod.DELETE,
            path=f'/user-api-key/{request.user_id}/{request.api_key}',
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

    def change_company_owner(self, user_id: str):
        """
        change_company_owner implementation
        """
        request = ChangeCompanyOwnerRequest(
            user_id=user_id,
        )

        response = self._api_call(
            method=HTTPMethod.POST, path=f'/company-owner/{request.user_id}'
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

    def delete_company_user(self, user_id: str):
        """
        delete a user in the company
        """

        request = DeleteCompanyUserRequest(user_id=user_id)

        response = self._api_call(
            method=HTTPMethod.DELETE, path=f'/company-user/{request.user_id}'
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

    def get_integration_credentials(
        self, credentials_id: str
    ) -> IntegrationCredentials:
        """
        get_integration_credentials implementation
        """

        response = self._api_call(
            method=HTTPMethod.GET,
            path=f'/integration/credentials/{credentials_id}',
        )

        if response.status_code != 200:
            self._default_exception_handler(response, SDKClientException)

        # Parse as the parent class
        credentials = parse_raw_as(IntegrationCredentials, response.content)

        # Cast to the correct subclass
        if credentials.type == ExternalIntegration.AWS:
            return parse_raw_as(AWSCredentials, response.content)

        raise NotImplementedError(f'{credentials.type} is not supported')

    def get_all_project_integration_credentials(
        self, project_id: str
    ) -> List[IntegrationCredentials]:
        """
        get_all_project_integration_credentials implementation
        """

        response = self._api_call(
            method=HTTPMethod.GET,
            path=f'/project/{project_id}/integration-credentials',
        )

        if response.status_code != 200:
            self._default_exception_handler(response, SDKClientException)

        # Parse as list of dicts, then cast each one to the subclass
        credentials: List[Dict] = response.json()

        casted_credentials: List[IntegrationCredentials] = []

        for cred in credentials:
            # Parse as parent class to access the 'type' field
            generic: IntegrationCredentials = IntegrationCredentials.parse_obj(
                cred
            )

            # Cast to the correct subclass
            if generic.type == ExternalIntegration.AWS:
                casted_credentials.append(AWSCredentials.parse_obj(cred))
            elif generic.type == ExternalIntegration.GCP:
                casted_credentials.append(GCPCredentials.parse_obj(cred))
            elif generic.type == ExternalIntegration.AZURE:
                casted_credentials.append(AzureCredentials.parse_obj(cred))
            else:
                raise NotImplementedError(f'{generic.type} is not supported')

        return casted_credentials

    def delete_integration_credentials(self, credentials_id: str):
        """
        delete_integration_credentials implementation
        """

        response = self._api_call(
            method=HTTPMethod.DELETE,
            path=f'/integration/credentials/{credentials_id}',
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

    def set_integration_credentials_as_default(self, credentials_id: str):
        """
        set_integration_credentials_as_default implementation
        """

        response = self._api_call(
            method=HTTPMethod.POST,
            path=f'/integration/credentials/{credentials_id}/default',
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

    def create_aws_integration_credentials(
        self, name: str, default: bool, project_id: str, role_arn: str
    ) -> SecretAWSCredentials:
        """
        create_aws_integration_credentials implementation
        """

        request = CreateAWSIntegrationCredentialsRequest(
            name=name,
            default=default,
            project_id=project_id,
            role_arn=role_arn,
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/integration/aws/credentials',
            json_payload=request.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

        return parse_raw_as(SecretAWSCredentials, response.content)

    def create_gcp_integration_credentials(
        self,
        name: str,
        default: bool,
        project_id: str,
        service_account_info_json: str,
    ) -> GCPCredentials:
        """
        create_gcp_integration_credentials implementation
        """

        try:
            account_info = GCPAccountInfo.parse_obj(
                json.loads(service_account_info_json)
            )
        except Exception as e:
            raise SDKClientException('Invalid credentials format') from e

        request = CreateGCPIntegrationCredentialsRequest(
            name=name,
            default=default,
            project_id=project_id,
            account_info=account_info,
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/integration/gcp/credentials',
            json_payload=request.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

        return parse_raw_as(GCPCredentials, response.content)

    def create_azure_integration_credentials(
        self,
        name: str,
        default: bool,
        project_id: str,
        service_principal_credentials_json: str,
    ) -> AzureCredentials:
        """
        create_azure_integration_credentials implementation
        """

        try:
            credentials = AzureSPCredentials.parse_obj(
                json.loads(service_principal_credentials_json)
            )
        except Exception as e:
            raise SDKClientException('Invalid credentials format') from e

        request = CreateAzureIntegrationCredentialsRequest(
            name=name,
            default=default,
            project_id=project_id,
            credentials=credentials,
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/integration/azure/credentials',
            json_payload=request.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

        return parse_raw_as(AzureCredentials, response.content)

    def set_retrain_trigger(
        self,
        model_id: str,
        trigger: Optional[RetrainTrigger],
    ):
        """
        set_retrain_trigger implementation
        """

        if trigger is None:
            response = self._api_call(
                method=HTTPMethod.DELETE,
                path=f'/model/{model_id}/retrain-trigger',
            )
        else:
            response = self._api_call(
                method=HTTPMethod.POST,
                path=f'/model/{model_id}/retrain-trigger',
                json_payload=trigger.json(),
            )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

    def test_retrain_trigger(self, model_id: str, trigger: RetrainTrigger):
        """
        test_retrain_trigger implementation
        """
        payload = TestRetrainTriggerRequest(
            model_id=model_id,
            retrain_trigger=trigger,
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/test-retrain-trigger',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

    def retrain_model(
        self,
        model_id: str,
    ) -> str:
        """
        retrain_model implementation
        """

        payload = RetrainModelRequest(
            model_id=model_id,
        )

        response = self._api_call(
            method=HTTPMethod.POST,
            path='/retrain-model',
            json_payload=payload.json(),
        )

        if response.status_code != 200:
            self._default_exception_handler(
                response=response, exception_type=SDKClientException
            )

        return response.json()
