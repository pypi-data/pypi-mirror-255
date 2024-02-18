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
    __request__: SearchKeyword,
    slug: str,
) -> SearchKeyword:
    body = __request__

    m = ApiRequest(
        method="PUT",
        path="/api/v1/keywords/{slug}/".format(
            slug=slug,
        ),
        content_type="application/json",
        body=body,
        headers=self._only_provided({}),
        query_params=self._only_provided({}),
        cookies=self._only_provided({}),
    )
    return self.make_request(
        {
            "200": {
                "application/json": SearchKeyword,
            },
        },
        m,
    )
