from typing import List, Optional

from ml3_platform_sdk.core.client_impl import ML3PlatformClientImpl
from ml3_platform_sdk.enums import (
    ApiKeyExpirationTime,
    DetectionEventSeverity,
    DetectionEventType,
    JobStatus,
    ModelMetricName,
    MonitoringTarget,
    StoragePolicy,
    SuggestionType,
    TaskType,
    UserCompanyRole,
    UserProjectRole,
)
from ml3_platform_sdk.models import (
    KPI,
    ApiKey,
    AzureCredentials,
    Company,
    CompanyUser,
    DataSchema,
    DataSource,
    DetectionEventAction,
    DetectionEventRule,
    GCPCredentials,
    IntegrationCredentials,
    Job,
    Model,
    PredictionDataSourceInfo,
    Project,
    RetrainingReport,
    RetrainTrigger,
    SecretAWSCredentials,
    SuggestionInfo,
    Task,
    TaskCostInfo,
)


class ML3PlatformClient(ML3PlatformClientImpl):
    """
    Client class is the single point of interaction with ML cube
    Platform APIs, it is initialized providing the `url` and the User
    `api_key`.
    Every operation is performed verifying the API Key and the
    permissions associated to the User that own that key.

    ### Methods categories
    There are the following types of methods:

    - **entity creation:** create the entity and return its identifier.
    It is used in the other methods to indicate the entity.
    - **entity update:** modify the entity but do not return anything.
    - **entity getters:** return a Pydantic `BaseModel` with the
    required entity.
    - **entity show:** print to the stdout the entity, but they do not
    return anything.
    - **entity delete:** delete the entity
    - **job submission:** submit a job on ML cube Platform that will
    take some time. They return the job identifier that can be used to
    monitor its state.
    - **job waiters:** given a job id wait the until the job is
    completed

    ### Exceptions
    The Client class raises only exceptions that are subclasses of
    `SDKClientException`.
    The exception has two fields that you can share with ML cube Support
    to get help in identifying the problem:

    - **error_code:** unique identifier of the error
    - **error_message:** message that explain the error

    The page is structured in different blocks of methods, one for each
    entity.

    """

    def __init__(self, url: str, api_key: str):
        super().__init__(url, api_key)

    def create_company(self, name: str, address: str, vat: str) -> str:
        """
        Create a company for the User, this method works only is the
        User has not a company yet.
        After the Company is created the User is the Company Owner.

        Args:
            name: the name of the company
            address: the address of the company
            vat: the vat of the company

        Returns:
            company_id: `str`

        Raises:
            `CreateCompanyException`
        """
        return super().create_company(name=name, address=address, vat=vat)

    def get_company(self) -> Company:
        """
        Returns the company of the User

        Returns:
            company: `Company`

        Raises:
            `SDKClientException`
        """
        return super().get_company()

    def update_company(
        self, name: Optional[str], address: Optional[str], vat: Optional[str]
    ) -> None:
        """
        Update company information.

        Empty values will not be updated.

        **Allowed Roles**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            name: new the of the company
            address: new billing address for the company
            vat: new vat of the company

        Raises:
            `UpdateCompanyException`
        """
        return super().update_company(name=name, address=address, vat=vat)

    def create_project(
        self,
        name: str,
        description: Optional[str],
        default_storage_policy: StoragePolicy,
    ) -> str:
        """
        Create a project inside the company. You don't need to specify
        the company because a User belongs only to one company and it
        is retrieved automatically.

        **Allowed Roles**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`
        Args:
            name: the name of the project
            description: optional description of the project
            default_storage_policy: represents the default policy to
                use for storing data in ML cube Platform

        Returns:
            project_id: `str`

        Raises:
            `CreateProjectException`
        """
        return super().create_project(
            name=name,
            description=description,
            default_storage_policy=default_storage_policy,
        )

    def get_projects(self) -> List[Project]:
        """
        Get the list of all projects in the company the User has
        permissions to view.

        Returns:
            projects_list: `List[Project]`

        Raises:
            `SDKClientException`
        """
        return super().get_projects()

    def get_project(self, project_id: str) -> Project:
        """
        Get a project with the given id

        **Allowed Roles**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            project_id: project identifier
        Returns:
            project: `Project`

        Raises:
            `SDKClientException`
        """
        return super().get_project(project_id=project_id)

    def update_project(
        self,
        project_id: str,
        name: Optional[str],
        description: Optional[str],
        default_storage_policy: Optional[StoragePolicy],
    ) -> None:
        """
        Update project details.

        Empty values will not be updated.

        **Allowed Roles**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            project_id: project identifier
            name: new name of the project
            description: new description of the project
            default_storage_policy: represents the default policy to
                use for storing data in ML cube Platform
        Returns:
            project: `Project`

        Raises:
            `UpdateProjectException`
        """
        return super().update_project(
            project_id=project_id,
            name=name,
            description=description,
            default_storage_policy=default_storage_policy,
        )

    def show_projects(self) -> None:
        """
        Show a list all projects printing to stdout.

        **Example output:**
            ```
            Project ID                Name
            ------------------------  ----------
            6475f8c9ebac5081e529s63f  my project
            ```
        """
        super().show_projects()

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
        Create a task inside the project.

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`
        Args:
            project_id: the identifier of the project
            name: the name of the task
            tags: a list of tags associated with the task
            task_type: the type of the task. See `TaskType`
                documentation for more information
            cost_info: optional argument that specify the cost
                information of the task
            optional_target: True if the target value in not always
                available. This changes the behaviour and the detection
                phase of ML cube Platform that will analyse production
                data without considering the actual target

        Returns:
            task_id: `str`

        Raises:
            `CreateTaskException`
        """
        return super().create_task(
            project_id=project_id,
            name=name,
            tags=tags,
            task_type=task_type,
            cost_info=cost_info,
            optional_target=optional_target,
        )

    def update_task(
        self,
        task_id: str,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        cost_info: Optional[TaskCostInfo] = None,
    ):
        """
        Update task attributes.

        `None` parameters are ignored for the update.

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`
        Args:
            task_id: the identifier of the task
            name: the name of the task
            tags: a list of tags associated with the task. To remove
                all the tags then pass an empty list.
            cost_info: optional argument that specify the cost
                information of the task

        Raises:
            `UpdateTaskException`
        """
        super().update_task(
            task_id=task_id,
            name=name,
            tags=tags,
            cost_info=cost_info,
        )

    def get_tasks(self, project_id: str) -> List[Task]:
        """
        Get the list of the Tasks inside the project.

        Args:
            project_id: identifier of the project

        Returns:
            task_list: `List[Task]`

        Raises:
            `SDKClientException`
        """

        return super().get_tasks(project_id=project_id)

    def get_task(self, task_id: str) -> Task:
        """
        Get task by id.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            task_id: identifier of the task

        Returns:
            task: `Task`

        Raises:
            `SDKClientException`
        """

        return super().get_task(task_id=task_id)

    def show_tasks(self, project_id: str):
        """
        Show a list of tasks included in a project to stdout.

        Args:
            project_id: the identifier of a project

        **Example output:**
        ```
        Task ID                   Name     Type            Status     Status start date
        ------------------------  -------  --------------  --------   -----------------
        6476040d583201813ab4539a  my task  classification  OK         03-02-2023 10:14:06
        ```
        """
        super().show_tasks(project_id=project_id)

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
        Create a model inside the task.

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            task_id: the identifier of the task
            name: the name of the model
            version: the current version of the model
            metric_name: performance or error metric associated with
                the model
            retraining_cost: estimated costs in the Task currency to
                retrain the model. This information is used by the
                retraining tool to show gain-cost information.
                Default value is 0.0 meaning that the cost is negligible
            preferred_suggestion_type: preferred type of suggestion that
                will be computed to retrain the model
            resampled_dataset_size: size of the resampled dataset that
                will be proposed to retrain the model
                note: this parameter is required if
                `preferred_suggestion_type` is
                `SuggestionType.RESAMPLED_DATASET`

        Returns:
            model_id: `str` identifier of the created model

        Raises:
            `CreateModelException`
        """
        return super().create_model(
            task_id=task_id,
            name=name,
            version=version,
            metric_name=metric_name,
            retraining_cost=retraining_cost,
            preferred_suggestion_type=preferred_suggestion_type,
            resampled_dataset_size=resampled_dataset_size,
        )

    def get_models(self, task_id: str) -> List[Model]:
        """
        Get all models of a task.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`
        Args:
            task_id: identifier of the task

        Returns:
            models_list: `List[Model]`

        Raises:
            `SDKClientException`
        """

        return super().get_models(task_id=task_id)

    def get_model(self, model_id: str) -> Model:
        """
        Get model by id.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`
        Args:
            model_id: identifier of the model

        Returns:
            model: `Model`

        Raises:
            `SDKClientException`
        """

        return super().get_model(model_id=model_id)

    def get_model_by_name_and_version(
        self, task_id: str, model_name: str, model_version: str
    ) -> Model:
        """
        Get model by name and version.

        A Model can have multiple versions according to the updates and
        retraining done.
        This method allow to get the Model object by specifying its
        name and the version tag.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`
        Args:
            task_id: the identifier of the task
            model_name: the name of the model
            model_version: the version of the model

        Returns:
            model: `Model`

        Raises:
            `SDKClientException`
        """

        return super().get_model_by_name_and_version(
            task_id=task_id, model_name=model_name, model_version=model_version
        )

    def show_models(self, task_id: str) -> None:
        """
        Show a list of models included in a task to stdout.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            task_id: the identifier of the task

        **Example output:**
        ```
        Model Id                  Task Id                   Name                    Version    Status           Status start timestamp    Status insert date          Metric Name
        ------------------------  ------------------------  ----------------------  ---------  ---------------  ------------------------  --------------------------  --------------------
        64fecf7d323311ab78f17280  64fecf7c323311ab78f17262  model_local_experiment  v0.0.1     not_initialized                            2023-09-11 08:27:41.431000  ModelMetricName.RMSE
        ```
        """
        super().show_models(task_id=task_id)

    def get_suggestions_info(
        self, model_id: str, model_version: str
    ) -> List[SuggestionInfo]:
        """
        Retrieve suggestions associated with a model.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            model_id: the identifier of the model
            model_version: the version of the model

        Returns:
            suggestion_info_list: `List[SuggestionInfo]`

        Raises:
            `SDKClientException`
        """

        return super().get_suggestions_info(
            model_id=model_id, model_version=model_version
        )

    def show_suggestions(self, model_id: str, model_version: str) -> None:
        """
        Show the list of suggestions associated with a
        model printing them to stdout.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            model_id: the identifier of the model
            model_version: the version of the model

        **Example output:**
        ```
        Suggestion Id                     Executed    Timestamp
        --------------------------------  ----------  --------------------------
        79a8710c351c4b6a9ece7322e153f200  True        2023-08-21 10:54:40.386189
        ```

        Raises:
            `SDKClientException`
        """
        super().show_suggestions(
            model_id=model_id, model_version=model_version
        )

    def set_model_suggestion_type(
        self,
        model_id: str,
        preferred_suggestion_type: SuggestionType,
        resampled_dataset_size: Optional[int] = None,
    ):
        """
        Set model suggestion type.

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            model_id: the identifier of the task
            preferred_suggestion_type: preferred type of suggestion that
                will be computed to retrain the model
            resampled_dateset_size: size of the resampled dataset that
                will be proposed to retrain the model
                note: this parameter is required if
                `preferred_suggestion_type` is
                `SuggestionType.RESAMPLED_DATASET`

        Raises:
            `SetModelSuggestionTypeException`
        """
        return super().set_model_suggestion_type(
            model_id=model_id,
            preferred_suggestion_type=preferred_suggestion_type,
            resampled_dataset_size=resampled_dataset_size,
        )

    def update_model_version_by_suggestion_id(
        self,
        model_id: str,
        new_model_version: str,
        suggestion_id: str,
    ) -> str:
        """
        Update model version by suggestion id.
        To retrain the Model, ML cube Platform provides importance
        weights through a `SuggestionInfo`.
        After the retraining is completed, you use this method to
        create the new model version in ML cube Platform.
        By specifying the `suggestion_id`, ML cube Platform
        automatically knows which is the reference data the model is
        trained on.

        This request starts an operation pipeline that is
        executed by ML cube Platform.
        Thus, the method returns the identifier of the job that you can
        monitor to know its status and proceed with the other work
        using the method `wait_job_completion(job_id)`

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            model_id: the identifier of the model
            new_model_version: the new version of the model
            suggestion_id: the identifier of the suggestion

        Returns:
            job_id: `str` job identifier of the pipeline in execution

        Raises:
            `UpdateModelVersionException`
        """

        return super().update_model_version_by_suggestion_id(
            model_id=model_id,
            new_model_version=new_model_version,
            suggestion_id=suggestion_id,
        )

    def update_model_version_from_raw_data(
        self,
        model_id: str,
        new_model_version: str,
        features_data_source: DataSource,
        targets_data_source: DataSource,
    ) -> str:
        """
        Update model version by suggestion id.
        To retrain the Model, ML cube Platform provides importance
        weights through a `SuggestionInfo`.
        However, it is possible to train the model with new data that
        has been not already upload to ML cube Platform.
        After the retraining is completed, you use this method to
        create the new model version in ML cube Platform by
        specifying the data to load.

        This request starts an operation pipeline that is
        executed by ML cube Platform.
        Thus, the method returns the identifier of the job that you can
        monitor to know its status and proceed with the other work
        using the method `wait_job_completion(job_id)`

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            model_id: the identifier of the model
            new_model_version: the new version of the model
            dataset_type:  Dataset type describes the nature
                           of data stored (DatasetType)
            features_data_source: data source that contains features data
            targets_data_source: data source that contains targets data
        Returns:
            job_id: `str` job identifier of the pipeline in execution

        Raises:
            `UpdateModelVersionException`

        Returns the job_id associated to the pipeline
        """

        return super().update_model_version_from_raw_data(
            model_id=model_id,
            new_model_version=new_model_version,
            features_data_source=features_data_source,
            targets_data_source=targets_data_source,
        )

    def add_data_schema(self, task_id: str, data_schema: DataSchema) -> None:
        """
        Associate a data schema to a task.

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`


        Args:
            task_id: the identifier of the task
            data_schema: the data schema that characterize your task

        Raises:
            `AddDataSchemaException`
        """
        super().add_data_schema(task_id=task_id, data_schema=data_schema)

    def get_data_schema(self, task_id: str) -> DataSchema:
        """
        Get task data schema

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            task_id: identifier of the task

        Returns:
            data_schema: `DataSchema`

        Raises:
            `SDKClientException`
        """
        return super().get_data_schema(task_id=task_id)

    def show_data_schema(self, task_id: str):
        """
        Show data schema of associated with a task

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            task_id: identifier of the task

        Raises:
            `SDKClientException`

        **Example output:**


            Column name       Role     Type      Nullable
            ----------------  -------  --------  ----------
            sample_id         id       string    False
            timestamp         time_id  string    False
            sepallength       input    float     False
            sepalwidth        input    float     False
            petallength       input    float     False
            petalwidth        input    float     False
            class             target   category  False

        """
        super().show_data_schema(task_id=task_id)

    def add_historical_data(
        self,
        task_id: str,
        features_data_source: DataSource,
        targets_data_source: Optional[DataSource] = None,
    ) -> str:
        """
        Add a batch of historical data for the Task.

        This request starts an operation pipeline that is
        executed by ML cube Platform.
        Thus, the method returns the identifier of the job that you can
        monitor to know its status and proceed with the other work
        using the method `wait_job_completion(job_id)`

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            task_id: the identifier of the task
            features_data_source: data source that contains features data
            targets_data_source: data source that contains targets data

        Returns:
            job_id: `str` identifier of the submitted job

        Raises:
            `AddHistoricalDataException`
        """
        return super().add_historical_data(
            task_id,
            features_data_source=features_data_source,
            targets_data_source=targets_data_source,
        )

    def add_model_reference(
        self,
        model_id: str,
        features_data_source: DataSource,
        targets_data_source: DataSource,
    ) -> str:
        """
        Add a batch of reference data associated with a given model.

        This request starts an operation pipeline that is
        executed by ML cube Platform.
        Thus, the method returns the identifier of the job that you can
        monitor to know its status and proceed with the other work
        using the method `wait_job_completion(job_id)`

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            model_id: the identifier of the model
            dataset_type:  Dataset type describes the nature of data stored
            features_data_source: data source that contains features data
            targets_data_source: data source that contains targets data

        Returns:
            job_id: `str` identifier of the submitted job

        Raises:
            `AddModelReferenceException`
        """

        return super().add_model_reference(
            model_id=model_id,
            features_data_source=features_data_source,
            targets_data_source=targets_data_source,
        )

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
        Add a batch of production data associated with a given task.

        This request starts an operation pipeline that is
        executed by ML cube Platform.
        Thus, the method returns the identifier of the job that you can
        monitor to know its status and proceed with the other work
        using the method `wait_job_completion(job_id)`

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            task_id: the identifier of the task
            dataset_type:  Dataset type describes the nature of data stored
            features_data_source: data source that contains features data. It can be None if you upload other kinds of data
            targets_data_source: data source that contains targets data. It can be None if you upload other kinds of data
            predictions_data_sources: list of data sources for each models' predictions. It can be None if you upload other kinds of data
        Returns:
            job_id: `str` identifier of the submitted job

        Raises:
            `AddProductionDataException`
        """

        return super().add_production_data(
            task_id=task_id,
            features_data_source=features_data_source,
            targets_data_source=targets_data_source,
            predictions_data_sources=predictions_data_sources,
        )

    def create_kpi(self, project_id: str, name: str) -> str:
        """
        Create a KPI.

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            project_id: the identifier of the project
            name: the name of the kpi

        Returns:
            kpi_id: `str` identifier of the created kpi

        Raises:
            `CreateKpiException`
        """
        return super().create_kpi(
            project_id=project_id,
            name=name,
        )

    def get_kpi(self, kpi_id: str) -> KPI:
        """
        Get kpi by id.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`
        Args:
            kpi_id: identifier of the kpi

        Returns:
            kpi: `KPI`

        Raises:
            `SDKClientException`
        """

        return super().get_kpi(kpi_id=kpi_id)

    def get_kpis(self, project_id: str) -> List[KPI]:
        """
        Get all kpis of a project.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`
        Args:
            project_id: identifier of the project

        Returns:
            kpis_list: `List[KPI]`

        Raises:
            `SDKClientException`
        """

        return super().get_kpis(project_id=project_id)

    def show_kpis(self, project_id: str) -> None:
        """
        Show the list of KPIs included in a project to stdout.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            project_id: the identifier of the project

        **Example output:**
        ```
        KPI Id                    Project Id                Name                    Status           Status start timestamp    Status insert date
        ------------------------  ------------------------  ----------------------  ---------------  ------------------------  --------------------------
        64fecf7d323311ab78f17280  64fecf7c323311ab78f17262  model_local_experiment  not_initialized                            2023-09-11 08:27:41.431000
        ```
        """
        super().show_kpis(project_id=project_id)

    def add_kpi_data(
        self,
        project_id: str,
        kpi_id: str,
        kpi_data_source: DataSource,
    ) -> str:
        """
        Add a batch of a given kpi with the given project.

        This request starts an operation pipeline that is
        executed by ML cube Platform.
        Thus, the method returns the identifier of the job that you can
        monitor to know its status and proceed with the other work
        using the method `wait_job_completion(job_id)`

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            project_id: the identifier of the project
            kpi_id: the identifier of the kpi
            kpi_data_source: data source that contains data.
        Returns:
            job_id: `str` identifier of the submitted job

        Raises:
            `AddKPIDataException`
        """

        return super().add_kpi_data(
            project_id=project_id,
            kpi_id=kpi_id,
            kpi_data_source=kpi_data_source,
        )

    def compute_retraining_report(self, model_id: str) -> str:
        """
        Compute the retraining report for a given model

        This request starts an operation pipeline that is
        executed by ML cube Platform.
        Thus, the method returns the identifier of the job that you can
        monitor to know its status and proceed with the other work
        using the method `wait_job_completion(job_id)`

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            model_id: the identifier of the model

        Returns:
            job_id: `str` identifier of the submitted job

        Raises:
            `ComputeRetrainingReportException`
        """
        return super().compute_retraining_report(model_id=model_id)

    def get_retraining_report(
        self,
        model_id: str,
    ) -> RetrainingReport:
        """
        For a given model id, get the sample weights computed
        and additional information about them included in
        the retraining report

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            model_id: the identifier of the model

        Returns:
            retraining_report: `RetrainingReport`

        Raises:
            `GetRetrainingReportException`
        """
        return super().get_retraining_report(
            model_id=model_id,
        )

    def get_jobs(
        self,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        model_id: Optional[str] = None,
        status: Optional[JobStatus] = None,
        job_id: Optional[str] = None,
    ) -> List[Job]:
        """
        Get current jobs information.
        Jobs can be filtered by project_id, task_id, model_id or status.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            project_id: the project_id to filter job.
                If ``None`` job of every project will be returned
            task_id: the task_id to filter job.
                If ``None`` job of every task will be returned
            model_id: the model_id to filter job.
                If ``None`` job of every model will be returned
            status: the status to filter job.
                If ``None`` job with every status will be retrieved
            job_id: id of the job to filter.
                If ``None`` job with every id will be retrieved

        Returns:
            jobs_list: `List[Job]`

        Raises:
            `SDKClientException`

        """
        return super().get_jobs(
            project_id=project_id,
            task_id=task_id,
            model_id=model_id,
            status=status,
            job_id=job_id,
        )

    def get_job(
        self,
        job_id: str,
    ) -> Job:
        """
        Get current job information.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            job_id: id of the job to retrieve

        Returns:
            job: `Job`

        Raises:
            `SDKClientException`
        """
        return super().get_job(
            job_id=job_id,
        )

    def show_jobs(self) -> None:
        """
        Show current job information to stdout.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Raises:
            `SDKClientException`
        """
        super().show_jobs()

    def get_detection_event_rules(
        self,
        task_id: str,
    ) -> List[DetectionEventRule]:
        """
        Get all detection event rules of a given task.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            task_id: id of the task for which you want to retrieve
            the detection event rules

        Returns:
            rules_list: `List[DetectionEventRule]`

        Raises:
            `SDKClientException`
        """
        return super().get_detection_event_rules(
            task_id=task_id,
        )

    def get_detection_event_rule(
        self,
        rule_id: str,
    ) -> DetectionEventRule:
        """
        Get a detection event rule by id.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            rule_id: id of the rule

        Returns:
            rule: `DetectionEventRule`

        Raises:
            `SDKClientException`
        """

        return super().get_detection_event_rule(rule_id=rule_id)

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
        Create a detection event rule.

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            name: the name of the rule
            task_id: the id of the task to which the rule belongs.
                The rule will only respond to detection events
                generated by this task.
            model_name: the name of the model, only required if
                monitoring_target is set to MODEL.
            detection_event_type: the type of detection event that
                this rule should respond to.
            monitoring_target: the type of monitoring target that
                this rule should respond to.
            severity: the level of severity of the detection event
                that this rule should respond to.
            actions: the list of actions to execute, in order,
                when the conditions of the rule are matched.

        Returns:
            rule_id: `str`

        Raises:
            `CreateDetectionEventRuleException`
        """

        return super().create_detection_event_rule(
            name=name,
            task_id=task_id,
            model_name=model_name,
            severity=severity,
            detection_event_type=detection_event_type,
            monitoring_target=monitoring_target,
            actions=actions,
        )

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
        Update a detection event rule.

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            rule_id: the id of the rule to update
            name: the name of the rule. If None, keeps the existing value.
            model_name: the name of the model, only required if
                monitoring_target is set to MODEL.
                If None, keeps the existing value.
            detection_event_type: the type of detection event that this
                rule should respond to. If None, keeps the existing value.
            monitoring_target: the type of monitoring target that this
                rule should respond to. If None, keeps the existing value.
            severity: the level of severity of the detection event that
                this rule should respond to. If None, keeps the
                existing value.
            actions: the list of actions to execute, in order, when the
                conditions of the rule are matched. If None,
                 keeps the existing value.

        Raises:
            `CreateDetectionEventRuleException`
        """

        return super().update_detection_event_rule(
            rule_id=rule_id,
            name=name,
            model_name=model_name,
            severity=severity,
            detection_event_type=detection_event_type,
            monitoring_target=monitoring_target,
            actions=actions,
        )

    def delete_detection_event_rule(self, rule_id: str):
        """
        Delete a detection event rule by id.

        **Allowed Roles:**

            - At least `PROJECT_EDIT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            rule_id: id of the rule to delete

        Raises:
            `SDKClientException`
        """

        return super().delete_detection_event_rule(rule_id=rule_id)

    def wait_job_completion(self, job_id: str, max_wait_timeout: int = 600):
        """
        Wait that the ML cube Platform job terminates successfully its
        execution.

        Note that this method stops the execution.

        **Allowed Roles:**

            - At least `PROJECT_VIEW` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            job_id: identifier of the job
            max_wait_timeout: maximum amount of seconds to wait before
                launching `JobWaitTimeoutException`

        Raises:

            - `JobWaitTimeoutException` when the maximum timeout time
                is reached
            - `JobNotFoundException` when the requested job does not
                exist
            - `JobFailureException` when the requested job is failed
        """
        return super().wait_job_completion(
            job_id=job_id, max_wait_timeout=max_wait_timeout
        )

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
        Creates a new User in the company.

        **Allowed Roles:**

            - `COMPANY_OWNER`

        Args:
            name: name of the user
            surname: surname of the user
            username: username of the user
            password: temporary password for the user. It will change
                this at the first login
            email: email of the user
            company_role: role of the user inside the company

        Returns:
            user_id: `str`

        Raises:
            `SDKClientException`
        """

        return super().create_company_user(
            name=name,
            surname=surname,
            username=username,
            password=password,
            email=email,
            company_role=company_role,
        )

    def get_company_users(self) -> List[CompanyUser]:
        """
        Returns the list of users in the company.

        **Allowed Roles:**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`
            - `COMPANY_USER`

        Returns:
            users_list: `List[CompanyUser]`

        Raises:
            `SDKClientException`
        """

        return super().get_company_users()

    def change_user_company_role(
        self, user_id: str, company_role: UserCompanyRole
    ):
        """
        Change the company role of a user in the company.

        **Allowed Roles:**

            - `COMPANY_OWNER`: can change the roles of all the Users
            - `COMPANY_ADMIN`: can change only the roles of all the
                Users apart from other Admins and the Owner

        Args:
            user_id: the user for which the role is updated
            company_role: the new role to assign

        Raises:
            `SDKClientException`
        """

        super().change_user_company_role(
            user_id=user_id, company_role=company_role
        )

    def show_company_users(self):
        """
        Show company users to stdout.

        **Allowed Roles:**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`
            - `COMPANY_USER`

        Raises:
            `SDKClientException`
        """

        super().show_company_users()

    def get_user_projects(self, user_id: str) -> List[Project]:
        """
        Returns a list of projects that the user can view.

        **Allowed Roles:**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`
            - `COMPANY_USER`

        Args:
            user_id: the user for which you want to see the list

        Returns:
            projects_list: `List[Project]`

        Raises:
            `SDKClientException`
        """

        return super().get_user_projects(user_id=user_id)

    def show_user_projects(self, user_id: str):
        """
        Shows the projects that the user can view to stdout.

        **Allowed Roles:**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`
            - `COMPANY_USER`

        Args:
            user_id: the user for which you want to see the list

        Raises:
            `SDKClientException`
        """

        super().show_user_projects(user_id=user_id)

    def add_user_project_role(
        self, user_id: str, project_id: str, project_role: UserProjectRole
    ):
        """
        Add a project role to the user for the given project.

        The User Project role can be assigned only to `COMPANY_USER`
        because Admin and Owner already have all the permission over
        projects.

        **Allowed Roles:**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            user_id: the user for which you want to see the list
            project_id: identifies the project
            project_role: the project role to assign

        Raises:
            `SDKClientException`
        """

        super().add_user_project_role(
            user_id=user_id, project_id=project_id, project_role=project_role
        )

    def delete_project_role(self, user_id: str, project_id: str):
        """
        Delete the role of the user for the given project.

        The User Project role can be deleted only for `COMPANY_USER`
        because Admin and Owner have all the permission over projects.

        **Allowed Roles:**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            user_id: the user for which you want to see the list
            project_id: identifies the project

        Raises:
            `SDKClientException`
        """

        super().delete_project_role(user_id=user_id, project_id=project_id)

    def get_api_keys(self) -> List[ApiKey]:
        """
        Returns a list of api keys the user has.

        **Allowed Roles:**

            - `COMPANY_USER`

        Returns:
            api_keys_list: `List[ApiKey]`

        Raises:
            `SDKClientException`
        """

        return super().get_api_keys()

    def show_api_keys(self):
        """
        Shows the list of api keys the user has to stdout.

        **Allowed Roles:**

            - `COMPANY_USER`

        Raises:
            `SDKClientException`

        """

        super().show_api_keys()

    def create_api_key(
        self, name: str, expiration_time: ApiKeyExpirationTime
    ) -> str:
        """
        Create a new api key for the user

        **Allowed Roles:**

            - `COMPANY_USER`

        Returns:
            name: the name of the api key
            expiration_time: the expiration time of the api key

        Raises:
            `SDKClientException`
        """

        return super().create_api_key(
            name=name, expiration_time=expiration_time
        )

    def delete_api_key(self, api_key: str):
        """
        Delete the api key of the user

        **Allowed Roles:**

            - `COMPANY_USER`

        Args:
            api_key: api key to delete

        Raises:
            `SDKClientException`
        """

        super().delete_api_key(api_key=api_key)

    def get_user_api_keys(self, user_id: str) -> List[ApiKey]:
        """
        Get the list of api keys a user has.

        **Allowed Roles:**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            user_id: the user to get his api keys

        Raises:
            `SDKClientException`
        """

        return super().get_user_api_keys(user_id=user_id)

    def show_user_api_keys(self, user_id: str):
        """
        Shows the list of api keys a user has to stdout.

        **Allowed Roles:**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            user_id: the user to get his api keys

        Raises:
            `SDKClientException`
        """

        super().show_user_api_keys(user_id=user_id)

    def create_user_api_key(
        self, user_id: str, name: str, expiration_time: ApiKeyExpirationTime
    ) -> str:
        """
        Create a new api key for the user.

        **Allowed Roles:**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            user_id: the user to create a new api key
            name: the name of the api key
            expiration_time: the expiration time of the api key

        Returns:
            api_key: the new created api key for the user

        Raises:
            `SDKClientException`
        """

        return super().create_user_api_key(
            user_id=user_id, name=name, expiration_time=expiration_time
        )

    def delete_user_api_key(self, user_id: str, api_key: str):
        """
        Delete the api key of the user

        **Allowed Roles:**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`: cannot delete the api key of another
                Admin

        Args:
            user_id: the user to delete an api key
            api_key: the api key to delete

        Raises:
            `SDKClientException`
        """

        super().delete_user_api_key(user_id=user_id, api_key=api_key)

    def change_company_owner(self, user_id: str):
        """
        Change the company owner role from the requesting user to the
        other user.

        **Allowed Roles:**

            - `COMPANY_OWNER`

        Args:
            user_id: the user that become Company Owner

        Raises:
            `SDKClientException`
        """

        super().change_company_owner(user_id=user_id)

    def delete_company_user(self, user_id: str):
        """
         Delete a user from the company.

        **Allowed Roles:**

            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`: cannot delete other company admins

        Args:
            user_id: the user to delete

        Raises:
            `SDKClientException`
        """

        super().delete_company_user(user_id=user_id)

    def get_integration_credentials(
        self,
        credentials_id: str,
    ) -> IntegrationCredentials:
        """
        Get the credentials with the given id for 3rd party service
        provider integration.

        **Allowed Roles:**

            - At least `WORK_ON_PROJECT` for the project where the
            credentials have been configured
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            credentials_id: id of the integration credentials to
            retrieve.

        Returns:
            credentials: `IntegrationCredentials`

        Raises:
            `SDKClientException`
        """
        return super().get_integration_credentials(
            credentials_id=credentials_id,
        )

    def get_all_project_integration_credentials(
        self,
        project_id: str,
    ) -> List[IntegrationCredentials]:
        """
        Get the list of credentials for 3rd party service provider
        integrations that are currently configured in a project.

        **Allowed Roles:**

            - At least `WORK_ON_PROJECT` for that project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            project_id: id of the project for which all configured
            credentials should be retrieved.

        Returns:
            credentials_list: `List[IntegrationCredentials]`

        Raises:
            `SDKClientException`
        """
        return super().get_all_project_integration_credentials(
            project_id=project_id,
        )

    def delete_integration_credentials(self, credentials_id: str):
        """
         Delete credentials for the integration with a 3rd party
         service provider.

        **Allowed Roles:**

            - At least `UPDATE_PROJECT_INFORMATION` for the project
            where the credentials have been configured
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`: cannot delete other company admins

        Args:
            credentials_id: id of the integration credentials to
            delete.

        Raises:
            `SDKClientException`
        """

        super().delete_integration_credentials(credentials_id=credentials_id)

    def set_integration_credentials_as_default(self, credentials_id: str):
        """
         Set the credentials with the given id as default for 3rd party
         service provider integration.

        **Allowed Roles:**

            - At least `UPDATE_PROJECT_INFORMATION` for the project
            where the credentials have been configured
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            credentials_id: id of the integration credentials to
            set as default.

        Raises:
            `SDKClientException`
        """

        super().set_integration_credentials_as_default(
            credentials_id=credentials_id,
        )

    def create_aws_integration_credentials(
        self, name: str, default: bool, project_id: str, role_arn: str
    ) -> SecretAWSCredentials:
        """
        Create credentials to integrate with AWS. Returns an object
        that contains the external_id you will need to configure in
        your trust policy.

        **Allowed Roles:**

            - At least `UPDATE_PROJECT_INFORMATION` for the project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            name: a simple name to identify this set of credentials
            default: whether to use these credentials by default when
                using an AWS integration
            project_id: the project in which these credentials will
                be configured
            role_arn: the ARN of the IAM role that will be assumed by ML
                cube Platform

        Returns:
            credentials: `SecretAWSCredentials`

        Raises:
            `SDKClientException`
        """
        return super().create_aws_integration_credentials(
            name=name,
            default=default,
            project_id=project_id,
            role_arn=role_arn,
        )

    def create_gcp_integration_credentials(
        self,
        name: str,
        default: bool,
        project_id: str,
        service_account_info_json: str,
    ) -> GCPCredentials:
        """
        Create credentials to integrate with GCP.

        **Allowed Roles:**

            - At least `UPDATE_PROJECT_INFORMATION` for the project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            name: a simple name to identify this set of credentials
            default: whether to use these credentials by default when
                using an AWS integration
            project_id: the project in which these credentials will
                be configured
            service_account_info_json: the json-encoded string
                containing the key of the service account

        Returns:
            credentials: `GCPCredentials`

        Raises:
            `SDKClientException`
        """
        return super().create_gcp_integration_credentials(
            name=name,
            default=default,
            project_id=project_id,
            service_account_info_json=service_account_info_json,
        )

    def create_azure_integration_credentials(
        self,
        name: str,
        default: bool,
        project_id: str,
        service_principal_credentials_json: str,
    ) -> AzureCredentials:
        """
        Create credentials to integrate with Azure.

        **Allowed Roles:**

            - At least `UPDATE_PROJECT_INFORMATION` for the project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            name: a simple name to identify this set of credentials
            default: whether to use these credentials by default when
                using an AWS integration
            project_id: the project in which these credentials will
                be configured
            service_principal_credentials_json: the json-encoded string
                containing the credentials of the service principal

        Returns:
            credentials: `AzureCredentials`

        Raises:
            `SDKClientException`
        """
        return super().create_azure_integration_credentials(
            name=name,
            default=default,
            project_id=project_id,
            service_principal_credentials_json=service_principal_credentials_json,
        )

    def set_retrain_trigger(
        self,
        model_id: str,
        trigger: Optional[RetrainTrigger],
    ):
        """
        Set the retrain trigger for a given model.

        **Allowed Roles:**

            - At least `WORK_ON_PROJECT` for the project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            model_id: the id of the model
            trigger: the trigger to set. If you want to remove the
                trigger, set it to None

        Raises:
            `SDKClientException`
        """
        return super().set_retrain_trigger(
            model_id=model_id,
            trigger=trigger,
        )

    def test_retrain_trigger(self, model_id: str, trigger: RetrainTrigger):
        """
        Test the retrain trigger for a given model.


        **Allowed Roles:**

            - At least `WORK_ON_PROJECT` for the project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            model_id: the id of the model
            trigger: the trigger to test

        Raises:
            `SDKClientException`
        """
        return super().test_retrain_trigger(
            model_id=model_id,
            trigger=trigger,
        )

    def retrain_model(
        self,
        model_id: str,
    ) -> str:
        """
        Retrain a model via the configured retrain trigger.

        **Allowed Roles:**

            - At least `WORK_ON_PROJECT` for the project
            - `COMPANY_OWNER`
            - `COMPANY_ADMIN`

        Args:
            model_id: the id of the model

        Raises:
            `SDKClientException`
        """
        return super().retrain_model(
            model_id=model_id,
        )
