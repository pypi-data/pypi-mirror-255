from typing import Coroutine, Union

from feedancy.lib.adapter.base import HttpClientAdapter
from feedancy.lib.configuration import Configuration
from feedancy.lib.request import ApiRequest
from feedancy.lib.response import ApiResponse


class ApiClient:
    def __init__(self, configuration: Configuration, adapter: HttpClientAdapter):
        self._configuration = configuration
        self._adapter = adapter

    def call_api(
        self, api_request: ApiRequest
    ) -> Union[ApiResponse, Coroutine[None, None, ApiResponse]]:
        method = api_request.clone(
            path=self._configuration.host + api_request.path,
        )
        return self._adapter.call(method)
