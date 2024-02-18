from __future__ import annotations

import datetime
import pydantic
import typing

from pydantic import BaseModel

from feedancy.lib.base import BaseApi
from feedancy.lib.request import ApiRequest
from feedancy.lib import json


class SalaryDiagram(BaseModel):
    count: int
    salary: int


class SalaryDiagramResponse(BaseModel):
    data: typing.List[SalaryDiagram]
    error: typing.Union[str, None]


def make_request(
    self: BaseApi,
) -> SalaryDiagramResponse:
    body = None

    m = ApiRequest(
        method="GET",
        path="/api/v1/salary/diagram/".format(),
        content_type=None,
        body=body,
        headers=self._only_provided({}),
        query_params=self._only_provided({}),
        cookies=self._only_provided({}),
    )
    return self.make_request(
        {
            "200": {
                "application/json": SalaryDiagramResponse,
            },
        },
        m,
    )
