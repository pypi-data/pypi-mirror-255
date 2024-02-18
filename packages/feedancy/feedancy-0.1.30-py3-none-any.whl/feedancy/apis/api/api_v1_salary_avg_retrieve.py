from __future__ import annotations

import datetime
import pydantic
import typing

from pydantic import BaseModel

from feedancy.lib.base import BaseApi
from feedancy.lib.request import ApiRequest
from feedancy.lib import json


class AvgSalary(BaseModel):
    by_freelance: typing.Optional[typing.Union[int, None]] = None
    by_internship: typing.Optional[typing.Union[int, None]] = None
    by_vacancy: typing.Optional[typing.Union[int, None]] = None
    created_at: datetime.datetime
    id: int


class AvgSalaryResponse(BaseModel):
    data: AvgSalary
    error: str


def make_request(
    self: BaseApi,
) -> AvgSalaryResponse:
    body = None

    m = ApiRequest(
        method="GET",
        path="/api/v1/salary/avg/".format(),
        content_type=None,
        body=body,
        headers=self._only_provided({}),
        query_params=self._only_provided({}),
        cookies=self._only_provided({}),
    )
    return self.make_request(
        {
            "200": {
                "application/json": AvgSalaryResponse,
            },
        },
        m,
    )
