from __future__ import annotations

import datetime
import pydantic
import typing

from pydantic import BaseModel

from feedancy.lib.base import BaseApi
from feedancy.lib.request import ApiRequest
from feedancy.lib import json


class City(BaseModel):
    id: int
    name: str
    region: typing.Optional[typing.Union[int, None]] = None


def make_request(
    self: BaseApi,
) -> City:
    body = None

    m = ApiRequest(
        method="GET",
        path="/api/v1/city/".format(),
        content_type=None,
        body=body,
        headers=self._only_provided({}),
        query_params=self._only_provided({}),
        cookies=self._only_provided({}),
    )
    return self.make_request(
        {
            "200": {
                "application/json": City,
            },
        },
        m,
    )
