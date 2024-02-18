from __future__ import annotations

import datetime
import pydantic
import typing

from pydantic import BaseModel

from feedancy.lib.base import BaseApi
from feedancy.lib.request import ApiRequest
from feedancy.lib import json


class Currency(BaseModel):
    code: str
    id: int
    name: str


class Salary(BaseModel):
    currency: Currency
    id: int
    max_value: typing.Optional[typing.Union[int, None]] = None
    min_value: typing.Optional[typing.Union[int, None]] = None


def make_request(
    self: BaseApi,
) -> Salary:
    body = None

    m = ApiRequest(
        method="GET",
        path="/api/v1/salary/".format(),
        content_type=None,
        body=body,
        headers=self._only_provided({}),
        query_params=self._only_provided({}),
        cookies=self._only_provided({}),
    )
    return self.make_request(
        {
            "200": {
                "application/json": Salary,
            },
        },
        m,
    )
