from __future__ import annotations

import datetime
import pydantic
import typing

from pydantic import BaseModel

from feedancy.lib.base import BaseApi
from feedancy.lib.request import ApiRequest
from feedancy.lib import json


class Company(BaseModel):
    description: typing.Optional[typing.Union[str, None]] = None
    is_accredited: typing.Optional[typing.Union[bool, None]] = None
    link: typing.Optional[typing.Union[str, None]] = None
    logo: typing.Optional[typing.Union[str, None]] = None
    name: str
    size: typing.Optional[typing.Union[typing.Union[str, str, str], None]] = None
    sphere: typing.Optional[typing.Union[int, None]] = None


def make_request(
    self: BaseApi,
    __request__: Company,
    id: str,
) -> Company:
    body = __request__

    m = ApiRequest(
        method="PUT",
        path="/api/v1/company/{id}/".format(
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
                "application/json": Company,
            },
        },
        m,
    )
