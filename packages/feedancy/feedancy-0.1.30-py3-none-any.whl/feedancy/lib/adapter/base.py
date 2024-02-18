import abc

from feedancy.lib.request import ApiRequest
from feedancy.lib.response import ApiResponse


class HttpClientAdapter(abc.ABC):
    @abc.abstractmethod
    def call(self, api_request: ApiRequest) -> ApiResponse:
        pass
