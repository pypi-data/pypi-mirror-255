from enum import Enum


class TaskType(Enum):
    """
    **Fields:**

        - REGRESSION
        - CLASSIFICATION
    """

    REGRESSION = 'regression'
    CLASSIFICATION = 'classification'

    def __str__(self):
        return self.value


class TaskStatus(Enum):
    """
    **Fields:**

        - OK
        - WARNING
        - DRIFT
    """

    OK = 'ok'
    WARNING = 'warning'
    DRIFT = 'drift'

    def __str__(self):
        return self.value


class ModelStatus(Enum):
    """
    **Fields:**

        - NOT_INITIALIZED
        - OK
        - WARNING
        - DRIFT
    """

    NOT_INITIALIZED = 'not_initialized'
    OK = 'ok'
    WARNING = 'warning'
    DRIFT = 'drift'

    def __str__(self):
        return self.value


class KPIStatus(Enum):
    """
    **Fields:**

        - NOT_INITIALIZED
        - OK
        - WARNING
        - DRIFT
    """

    NOT_INITIALIZED = 'not_initialized'
    OK = 'ok'
    WARNING = 'warning'
    DRIFT = 'drift'

    def __str__(self):
        return self.value


class DatasetType(Enum):
    """
    **Fields:**

        - TABULAR
    """

    TABULAR = 'tabular'

    def __str__(self):
        return self.value


class StoringDataType(Enum):
    """
    **Fields:**

        - HISTORICAL
        - REFERENCE
        - PRODUCTION
    """

    HISTORICAL = 'historical'
    REFERENCE = 'reference'
    PRODUCTION = 'production'
    KPI = 'kpi'

    def __str__(self):
        return self.value


class FileType(Enum):
    """
    **Fields:**

        - CSV
        - JSON
    """

    CSV = 'csv'
    JSON = 'json'

    def __str__(self):
        return self.value


class JobStatus(Enum):
    """
    **Fields:**

        - IDLE
        - STARTING
        - RUNNING
        - COMPLETED
        - ERROR
    """

    IDLE = 'idle'
    STARTING = 'starting'
    RUNNING = 'running'
    COMPLETED = 'completed'
    ERROR = 'error'

    def __str__(self):
        return self.value


class UserCompanyRole(Enum):
    """
    **Fields:**

        - COMPANY_OWNER
        - COMPANY_ADMIN
        - COMPANY_USER
        - COMPANY_NONE
    """

    COMPANY_OWNER = "COMPANY_OWNER"
    COMPANY_ADMIN = "COMPANY_ADMIN"
    COMPANY_USER = "COMPANY_USER"
    COMPANY_NONE = "COMPANY_NONE"

    def __str__(self):
        return self.value


class UserProjectRole(Enum):
    """
    **Fields:**

        - PROJECT_ADMIN
        - PROJECT_USER
        - PROJECT_VIEW
    """

    PROJECT_ADMIN = "PROJECT_ADMIN"
    PROJECT_USER = "PROJECT_USER"
    PROJECT_VIEW = "PROJECT_VIEW"

    def __str__(self):
        return self.value


class DetectionEventSeverity(Enum):
    """
    **Fields:**

        - LOW
        - MEDIUM
        - HIGH
    """

    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

    def __str__(self):
        return self.value


class DetectionEventType(Enum):
    """
    **Fields:**

        - DRIFT
    """

    DRIFT = 'drift'

    def __str__(self):
        return self.value


class MonitoringTarget(Enum):
    """
    **Fields:**

        - MODEL
        - INPUT
        - CONCEPT
    """

    MODEL = 'model'
    INPUT = 'input'
    CONCEPT = 'concept'

    def __str__(self):
        return self.value


class DetectionEventActionType(Enum):
    """
    **Fields:**

        - DISCORD_NOTIFICATION
        - SLACK_NOTIFICATION

    """

    DISCORD_NOTIFICATION = 'discord_notification'
    SLACK_NOTIFICATION = 'slack_notification'
    EMAIL_NOTIFICATION = 'email_notification'
    TEAMS_NOTIFICATION = 'teams_notification'
    RETRAIN = 'retrain'

    def __str__(self):
        return self.value


class ModelMetricName(Enum):
    """
    Name of the model metrics that is associated with the model

    **Fields:**
        - RMSE
        - RSQUARE
    """

    RMSE = 'rmse'
    RSQUARE = 'rsquare'

    def __str__(self):
        return self.value


class SuggestionType(Enum):
    """
    Enum to specify the preferred
    type of suggestion

    **Fields:**
        - SAMPLE_WEIGHTS
        - RESAMPLED_DATASET
    """

    SAMPLE_WEIGHTS = 'sample_weights'
    RESAMPLED_DATASET = 'resampled_dataset'

    def __str__(self):
        return self.value


class ApiKeyExpirationTime(Enum):
    """
    **Fields:**

        - ONE_MONTH
        - THREE_MONTHS
        - SIX_MONTHS
        - ONE_YEAR
        - NEVER

    """

    ONE_MONTH = 'one_month'
    THREE_MONTHS = 'three_months'
    SIX_MONTHS = 'six_months'
    ONE_YEAR = 'one_year'
    NEVER = 'never'

    def __str__(self):
        return self.value


class ExternalIntegration(Enum):
    """
    An integration with a 3rd party service provider

    **Fields:**
        - AWS
        - GCP
        - AZURE
    """

    AWS = 'aws'
    GCP = 'gcp'
    AZURE = 'azure'

    def __str__(self):
        return self.value


class StoragePolicy(Enum):
    """
    Enumeration that specifies the storage policy for the data sent to
    ML cube Platform

    **Fields:**
        - MLCUBE: data are copied and stored into the ML cube Platform
            cloud
        - CUSTOMER: data are kept only in your cloud and ML cube
            Platform will access to this storage source every time
            it needs to read data
    """

    MLCUBE = 'mlcube'
    CUSTOMER = 'customer'

    def __str__(self):
        return self.value


class RetrainTriggerType(Enum):
    """
    Enumeration of the possible retrain triggers
    """

    AWS_EVENT_BRIDGE = 'aws_event_bridge'
    GCP_PUBSUB = 'gcp_pubsub'
    AZURE_EVENT_GRID = 'azure_event_grid'

    def __str__(self):
        return self.value


class Currency(Enum):
    """
    Currency of to use for the Task
    """

    EURO = 'euro'
    DOLLAR = 'dollar'

    def __str__(self):
        return self.value
