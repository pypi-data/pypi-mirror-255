class SDKClientException(Exception):
    """
    Base class for client sdk exceptions
    """

    def __init__(
        self,
        error_code: str = "UNEXPECTED",
        error_message: str = "An unexpected error occurred",
    ):
        self.error_code: str = error_code
        self.error_message: str = error_message


class CreateCompanyException(SDKClientException):
    """
    CreateCompanyException
    """


class UpdateCompanyException(SDKClientException):
    """
    UpdateCompanyException
    """


class CreateProjectException(SDKClientException):
    """
    CreateProjectException
    """


class UpdateProjectException(SDKClientException):
    """
    UpdateProjectException
    """


class CreateTaskException(SDKClientException):
    """
    CreateTaskException
    """


class UpdateTaskException(SDKClientException):
    """
    UpdateTaskException
    """


class CreateModelException(SDKClientException):
    """
    CreateModelException
    """


class AddDataSchemaException(SDKClientException):
    """
    AddDataSchemaException
    """


class AddHistoricalDataException(SDKClientException):
    """
    AddHistoricalDataException
    """


class AddModelReferenceException(SDKClientException):
    """
    AddModelReferenceException
    """


class SetModelSuggestionTypeException(SDKClientException):
    """
    SetModelSuggestionTypeException
    """


class UpdateModelVersionException(SDKClientException):
    """
    UpdateModelVersionException
    """


class AddProductionDataException(SDKClientException):
    """
    AddProductionDataException
    """


class ComputeRetrainingReportException(SDKClientException):
    """
    ComputeRetrainingReportException
    """


class GetRetrainingReportException(SDKClientException):
    """
    GetRetrainingReportException
    """


class UpdateDataSchemaException(SDKClientException):
    """
    UpdateDataSchemaException
    """


class JobWaitTimeoutException(SDKClientException):
    """
    JobWaitTimeoutException
    """


class JobNotFoundException(SDKClientException):
    """
    JobNotFoundException
    """


class JobFailureException(SDKClientException):
    """
    JobFailureException
    """


class CreateDetectionEventRuleException(SDKClientException):
    """
    CreateDetectionEventRuleException
    """


class UpdateDetectionEventRuleException(SDKClientException):
    """
    UpdateDetectionEventRuleException
    """


class CreateKPIException(SDKClientException):
    """
    CreateKPIEventRuleException
    """


class AddKPIDataException(SDKClientException):
    """
    AddKPIDataException
    """


class InvalidActionList(SDKClientException):
    """
    Exception raised when the detection event actions in the rule are
    not valid
    """
