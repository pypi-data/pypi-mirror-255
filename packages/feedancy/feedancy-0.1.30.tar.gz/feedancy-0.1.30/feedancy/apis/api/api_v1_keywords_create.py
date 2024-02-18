from __future__ import annotations

import datetime
import pydantic
import typing

from pydantic import BaseModel

from feedancy.lib.base import BaseApi
from feedancy.lib.request import ApiRequest
from feedancy.lib import json


class StopKeyword(BaseModel):
    name: str


class SearchKeyword(BaseModel):
    name: str
    slug: str
    stop_keywords: typing.List[StopKeyword]


def make_request(
    self: BaseApi,
    __request__: typing.List[SearchKeyword],
) -> typing.List[SearchKeyword]:
    body = __request__

    m = ApiRequest(
        method="POST",
        path="/api/v1/keywords/".format(),
        content_type="application/json",
        body=body,
        headers=self._only_provided({}),
        query_params=self._only_provided({}),
        cookies=self._only_provided({}),
    )
    return self.make_request(
        {
            "201": {
                "application/json": typing.List[SearchKeyword],
            },
        },
        m,
    )
