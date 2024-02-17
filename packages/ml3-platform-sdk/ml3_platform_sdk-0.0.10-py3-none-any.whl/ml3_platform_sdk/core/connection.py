import requests

from ml3_platform_sdk.core.enums import HTTPMethod


class Connection:
    """
    This class
    """

    initialized: bool = False

    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        self._headers = {'X-Api-Key': self.api_key}
        self.initialized = len(url) > 0 and len(api_key) > 0

    def _get_url(self, path):
        """
        Private method to build the url
        of the API request
        """
        return '/sdk/v1'.join([self.url, path])

    def send_api_request(
        self, method: HTTPMethod, path: str, timeout: int, **kwargs
    ):
        """
        Helper method to send an API request
        """
        return requests.request(
            method=str(method.value),
            url=self._get_url(path),
            headers=self._headers,
            timeout=timeout,
            **kwargs,
        )

    @staticmethod
    def send_data(presigned_url: dict, data_path: str):
        """
        Send file using a presigned URL
        """

        with open(data_path, 'rb') as file:
            files = {'file': file}

            # FIXME consider timeouts
            response = requests.post(  # pylint: disable=W3101
                presigned_url['url'], data=presigned_url['fields'], files=files
            )

            return response
