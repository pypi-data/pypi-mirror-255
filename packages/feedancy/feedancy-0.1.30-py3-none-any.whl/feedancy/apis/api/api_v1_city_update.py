from __future__ import annotations

import datetime
import pydantic
import typing

from pydantic import BaseModel

from feedancy.lib.base import BaseApi
from feedancy.lib.request import ApiRequest
from feedancy.lib import json


class City(BaseModel):
    name: str
    region: typing.Optional[typing.Union[int, None]] = None


def make_request(
    self: BaseApi,
    __request__: City,
    id: str,
) -> City:
    body = __request__

    m = ApiRequest(
        method="PUT",
        path="/api/v1/city/{id}/".format(
            id=id,
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
                "application/json": City,
            },
        },
        m,
    )
