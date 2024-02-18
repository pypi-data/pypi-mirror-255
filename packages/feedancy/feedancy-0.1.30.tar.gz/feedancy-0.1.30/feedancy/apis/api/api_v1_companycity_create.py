from __future__ import annotations

import datetime
import pydantic
import typing

from pydantic import BaseModel

from feedancy.lib.base import BaseApi
from feedancy.lib.request import ApiRequest
from feedancy.lib import json


class CompanyCity(BaseModel):
    city: int
    company: int


def make_request(
    self: BaseApi,
    __request__: CompanyCity,
) -> CompanyCity:
    body = __request__

    m = ApiRequest(
        method="POST",
        path="/api/v1/companycity/".format(),
        content_type="application/json",
        body=body,
        headers=self._only_provided({}),
        query_params=self._only_provided({}),
        cookies=self._only_provided({}),
    )
    return self.make_request(
        {
            "200": {
                "application/json": CompanyCity,
            },
        },
        m,
    )
