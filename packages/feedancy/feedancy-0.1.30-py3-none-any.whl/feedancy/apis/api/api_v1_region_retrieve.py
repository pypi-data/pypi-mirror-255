from __future__ import annotations

import datetime
import pydantic
import typing

from pydantic import BaseModel

from feedancy.lib.base import BaseApi
from feedancy.lib.request import ApiRequest
from feedancy.lib import json


class Region(BaseModel):
    country: int
    id: int
    name: str


def make_request(
    self: BaseApi,
) -> Region:
    body = None

    m = ApiRequest(
        method="GET",
        path="/api/v1/region/".format(),
        content_type=None,
        body=body,
        headers=self._only_provided({}),
        query_params=self._only_provided({}),
        cookies=self._only_provided({}),
    )
    return self.make_request(
        {
            "200": {
                "application/json": Region,
            },
        },
        m,
    )
