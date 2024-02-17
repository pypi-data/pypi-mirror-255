from pydantic import BaseModel


class StandardErrorResponse(BaseModel):
    """
    Standard error response
    """

    error_code: str
    error_message: str


class GetPresignedUrlResponse(BaseModel):
    """
    Get presigned url response
    """

    storing_process_id: str
    presigned_url: dict
    expiration_time: str
