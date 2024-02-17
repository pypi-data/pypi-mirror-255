from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from ml3_platform_sdk.core.enums import RawDataSourceType
from ml3_platform_sdk.enums import (
    ApiKeyExpirationTime,
    DatasetType,
    DetectionEventSeverity,
    DetectionEventType,
    FileType,
    MonitoringTarget,
    StoragePolicy,
    TaskType,
    UserCompanyRole,
    UserProjectRole,
)
from ml3_platform_sdk.models import DataSchema, RetrainTrigger, TaskCostInfo


class DataSourceInfo(BaseModel):
    """
    Support base model for data source info
    """

    dataset_type: DatasetType
    file_type: FileType
    data_source_type: RawDataSourceType
    remote_path: str
    credentials_id: Optional[str]
    storage_policy: Optional[StoragePolicy]


class CreateCompanyRequest(BaseModel):
    """
    CreateCompanyRequest
    """

    name: str
    address: str
    vat: str


class UpdateCompanyRequest(BaseModel):
    """
    UpdateCompanyRequest
    """

    name: Optional[str]
    address: Optional[str]
    vat: Optional[str]


class CreateProjectRequest(BaseModel):
    """
    CreateProjectRequest
    """

    name: str
    description: Optional[str]
    default_storage_policy: StoragePolicy


class UpdateProjectRequest(BaseModel):
    """
    UpdateProjectRequest
    """

    project_id: str
    name: Optional[str]
    description: Optional[str]
    default_storage_policy: Optional[StoragePolicy]


class GetTasksRequest(BaseModel):
    """
    GetTasksRequest
    """

    project_id: str


class GetTaskRequest(BaseModel):
    """
    GetTaskRequest
    """

    task_id: str


class CreateModelRequest(BaseModel):
    """
    CreateModelRequest
    """

    task_id: str
    name: str
    version: str
    metric_name: str
    retraining_cost: float
    preferred_suggestion_type: str
    resampled_dataset_size: Optional[int]


class SetModelSuggestionTypeRequest(BaseModel):
    """
    SetModelSuggestionTypeRequest
    """

    model_id: str
    preferred_suggestion_type: str
    resampled_dataset_size: Optional[int] = None


class GetModelsRequest(BaseModel):
    """
    Get models request model
    """

    task_id: str


class GetModelRequest(BaseModel):
    """
    Get model request model
    """

    model_id: str


class GetSuggestionsRequest(BaseModel):
    """
    Get models request model
    """

    model_id: str
    model_version: str


class UpdateModelVersionBySuggestionIDRequest(BaseModel):
    """
    Update Model Version By SuggestionInfo ID Request
    """

    model_id: str
    new_model_version: str
    suggestion_id: str


class UpdateModelVersionFromRawDataRequest(BaseModel):
    """
    Update Model Version From Raw Data Request
    """

    model_id: str
    new_model_version: str
    features_raw_data_storing_process_id: str
    targets_raw_data_storing_process_id: str


class AddHistoricalRequest(BaseModel):
    """
    Add Historical Request model

    `targets_raw_data_storing_process_id` is optional only when the Task
    has the `optional_target` attribute set to True i.e., when actually
    the target is allowed to be optional.
    """

    task_id: str
    features_raw_data_storing_process_id: str
    targets_raw_data_storing_process_id: Optional[str]


class AddProductionRequest(BaseModel):
    """
    Add Production Request model
    TODO sistemare docs
    """

    task_id: str
    features_raw_data_storing_process_id: Optional[str]
    targets_raw_data_storing_process_id: Optional[str]
    predictions_raw_data_storing_process_ids: List[str]


class AddReferenceRequest(BaseModel):
    """
    Add Reference Request model
    TODO sistemare docs
    """

    model_id: str
    features_raw_data_storing_process_id: str
    targets_raw_data_storing_process_id: str


class CreateDataSchemaRequest(BaseModel):
    """
    Create Data Schema Request model
    TODO sistemare docs
    """

    task_id: str
    data_schema: DataSchema


class CreateTaskRequest(BaseModel):
    """
    Create Data Schema Request model
    """

    project_id: str
    name: str
    tags: Optional[List[str]]
    task_type: TaskType
    cost_info: Optional[TaskCostInfo]
    optional_target: bool


class UpdateTaskRequest(BaseModel):
    """
    Update a task request payload
    """

    task_id: str
    name: Optional[str]
    tags: Optional[List[str]]
    cost_info: Optional[TaskCostInfo]


class ComputeRetrainingReportRequest(BaseModel):
    """
    request to compute retraining report
    """

    model_id: str


class GetRetrainingReportRequest(BaseModel):
    """
    request to obtain a previously
    computed retraining report
    """

    model_id: str


class GetDataSchemaRequest(BaseModel):
    """
    Get data schema request model
    """

    task_id: str


class GetJobRequest(BaseModel):
    """
    Get Job Information Request model
    """

    project_id: Optional[str]
    task_id: Optional[str]
    model_id: Optional[str]
    status: Optional[str]
    job_id: Optional[str]


class GetPresignedUrlRequest(BaseModel):
    """
    Get a presigned url for uploading new data
    into ML3 platform
    """

    project_id: Optional[str]
    task_id: Optional[str]
    dataset_type: str
    storing_data_type: str
    file_name: str
    file_type: str
    file_checksum: str
    data_category: Optional[str]
    model_id: Optional[str] = None
    kpi_id: Optional[str] = None


class CreateCompanyUserRequest(BaseModel):
    """
    TODO
    """

    name: str
    surname: str
    username: str
    password: str
    email: str
    company_role: UserCompanyRole


class RemoveUserFromCompanyRequest(BaseModel):
    """
    TODO
    """

    user_id: str


class AddUserToCompanyRequest(BaseModel):
    """
    TODO
    """

    user_id: str


class ChangeUserCompanyRoleRequest(BaseModel):
    """
    TODO
    """

    user_id: str
    company_role: UserCompanyRole


class AddUserProjectRoleRequest(BaseModel):
    """
    TODO
    """

    user_id: str
    project_id: str
    project_role: UserProjectRole


class DeleteUserProjectRoleRequest(BaseModel):
    """
    TODO
    """

    user_id: str
    project_id: str


class CreateApiKeyRequest(BaseModel):
    """
    TODO
    """

    name: str
    expiration_time: ApiKeyExpirationTime


class DeleteApiKeyRequest(BaseModel):
    """
    TODO
    """

    api_key: str


class GetUserApiRequest(BaseModel):
    """
    TODO
    """

    user_id: str


class CreateUserApiRequest(BaseModel):
    """
    TODO
    """

    user_id: str
    name: str
    expiration_time: ApiKeyExpirationTime


class DeleteUserApiKeyRequest(BaseModel):
    """
    TODO
    """

    user_id: str
    api_key: str


class ChangeCompanyOwnerRequest(BaseModel):
    """
    TODO
    """

    user_id: str


class CreateDetectionEventRuleRequest(BaseModel):
    """
    Create a rule that can be triggered by a detection event.
    """

    name: str
    task_id: str
    model_name: Optional[str]
    severity: DetectionEventSeverity
    detection_event_type: DetectionEventType
    monitoring_target: MonitoringTarget
    actions: List[Dict]


class UpdateDetectionEventRuleRequest(BaseModel):
    """
    Update a rule that can be triggered by a detection event.
    """

    rule_id: str
    name: Optional[str]
    model_name: Optional[str]
    severity: Optional[DetectionEventSeverity]
    detection_event_type: Optional[DetectionEventType]
    monitoring_target: Optional[MonitoringTarget]
    actions: Optional[List[Dict]]


class DeleteCompanyUserRequest(BaseModel):
    """
    Delete a user from the company
    """

    user_id: str


class CreateAWSIntegrationCredentialsRequest(BaseModel):
    """
    Request to create integration credentials for AWS on a
    given project.
    """

    name: str
    default: bool
    project_id: str
    role_arn: str


class GCPAccountInfo(BaseModel):
    """
    Information needed to assume a service role.
    """

    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str
    universe_domain: str


class AzureSPCredentials(BaseModel):
    """
    Information needed to authenticate as an SP.
    """

    app_id: str = Field(alias='appId')
    display_name: str = Field(alias='displayName')
    password: str
    tenant: str


class CreateGCPIntegrationCredentialsRequest(BaseModel):
    """
    Request to create integration credentials for GCP on a
    given project.
    """

    name: str
    default: bool
    project_id: str
    account_info: GCPAccountInfo


class CreateAzureIntegrationCredentialsRequest(BaseModel):
    """
    Request to create integration credentials for Azure on a
    given project.
    """

    name: str
    default: bool
    project_id: str
    credentials: AzureSPCredentials


class AddRemoteHistoricalDataRequest(BaseModel):
    """
    Add remote historical data request
    """

    task_id: str
    features_data_source_info: DataSourceInfo
    targets_data_source_info: Optional[DataSourceInfo]


class AddRemoteProductionDataRequest(BaseModel):
    """
    Add remote production data request
    """

    task_id: str
    features_data_source_info: Optional[DataSourceInfo]
    targets_data_source_info: Optional[DataSourceInfo]
    # it is a list of model_id and data source information
    predictions_data_source_info: List[Tuple[str, DataSourceInfo]]


class AddRemoteModelReferenceRequest(BaseModel):
    """
    Add remote model reference request
    """

    model_id: str
    features_data_source_info: DataSourceInfo
    targets_data_source_info: DataSourceInfo


class UpdateModelVersionFromRemoteRawDataRequest(BaseModel):
    """
    Update model version from remote raw data request
    """

    model_id: str
    new_model_version: str
    features_data_source_info: DataSourceInfo
    targets_data_source_info: DataSourceInfo


class CreateKPIRequest(BaseModel):
    """
    Create KPI request
    """

    project_id: str
    name: str


class GetKPIsRequest(BaseModel):
    """
    Get projects request model
    """

    project_id: str


class GetKPIRequest(BaseModel):
    """
    Get KPI request model
    """

    kpi_id: str


class AddKPIDataRequest(BaseModel):
    """
    Add KPI Data Request model
    """

    kpi_id: str
    kpi_raw_data_storing_process_id: str


class AddRemoteKPIDataRequest(BaseModel):
    """
    Add remote kpi data request
    """

    kpi_id: str
    kpi_data_source_info: DataSourceInfo


class TestRetrainTriggerRequest(BaseModel):
    """
    Test retrain trigger request
    """

    model_id: str
    retrain_trigger: RetrainTrigger


class RetrainModelRequest(BaseModel):
    """
    Retrain model request
    """

    model_id: str
