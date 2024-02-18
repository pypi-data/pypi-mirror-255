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


class InternshipContact(BaseModel):
    contact: typing.Union[Contact, None]
    internship: int


def make_request(
    self: BaseApi,
    __request__: InternshipContact,
    id: str,
) -> InternshipContact:
    body = __request__

    m = ApiRequest(
        method="PUT",
        path="/api/v1/internshipcontact/{id}/".format(
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
                "application/json": InternshipContact,
            },
        },
        m,
    )
