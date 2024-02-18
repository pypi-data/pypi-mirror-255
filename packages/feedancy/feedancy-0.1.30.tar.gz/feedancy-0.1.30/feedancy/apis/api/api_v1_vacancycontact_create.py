from __future__ import annotations

import datetime
import pydantic
import typing

from pydantic import BaseModel

from feedancy.lib.base import BaseApi
from feedancy.lib.request import ApiRequest
from feedancy.lib import json


class Contact(BaseModel):
    data: str
    name: typing.Optional[typing.Union[str, None]] = None
    type: str


class VacancyContact(BaseModel):
    contact: typing.Union[Contact, None]


def make_request(
    self: BaseApi,
    __request__: VacancyContact,
) -> VacancyContact:
    body = __request__

    m = ApiRequest(
        method="POST",
        path="/api/v1/vacancycontact/".format(),
        content_type="application/json",
        body=body,
        headers=self._only_provided({}),
        query_params=self._only_provided({}),
        cookies=self._only_provided({}),
    )
    return self.make_request(
        {
            "200": {
                "application/json": VacancyContact,
            },
        },
        m,
    )
