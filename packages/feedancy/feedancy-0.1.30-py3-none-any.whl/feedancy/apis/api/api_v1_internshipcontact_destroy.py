from __future__ import annotations

import datetime
import pydantic
import typing

from pydantic import BaseModel

from feedancy.lib.base import BaseApi
from feedancy.lib.request import ApiRequest
from feedancy.lib import json


def make_request(
    self: BaseApi,
    id: str,
) -> None:
    body = None

    m = ApiRequest(
        method="DELETE",
        path="/api/v1/internshipcontact/{id}/".format(
            id=id,
        ),
        content_type=None,
        body=body,
        headers=self._only_provided({}),
        query_params=self._only_provided({}),
        cookies=self._only_provided({}),
    )
    return self.make_request(
        {
            "204": {
                "default": None,
            },
        },
        m,
    )
