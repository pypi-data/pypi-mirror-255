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


class Currency(BaseModel):
    code: str
    name: str


class Salary(BaseModel):
    currency: Currency
    max_value: typing.Optional[typing.Union[int, None]] = None
    min_value: typing.Optional[typing.Union[int, None]] = None


class Vacancy(BaseModel):
    city: typing.Union[str, None]
    company: typing.Union[str, None]
    contacts: typing.Union[typing.List[VacancyContact], None]
    contract_type: typing.Optional[
        typing.Union[typing.Union[str, str, str], None]
    ] = None
    employment_format: typing.Optional[
        typing.Union[typing.Union[str, str, str], None]
    ] = None
    experience: typing.Optional[typing.Union[typing.Union[str, str, str], None]] = None
    external_id: str
    has_insurance: typing.Optional[typing.Union[bool, None]] = None
    has_portfolio: typing.Optional[typing.Union[bool, None]] = None
    has_test_task: typing.Optional[typing.Union[bool, None]] = None
    is_relocation_required: typing.Optional[typing.Union[bool, None]] = None
    link: str
    name: str
    publicated_at: typing.Optional[typing.Union[datetime.datetime, None]] = None
    raw_description: typing.Optional[typing.Union[str, None]] = None
    requirement: typing.Optional[typing.Union[str, None]] = None
    responsibility: typing.Optional[typing.Union[str, None]] = None
    salary: typing.Union[Salary, None]
    test_task_link: typing.Optional[typing.Union[str, None]] = None
    work_format: typing.Optional[typing.Union[typing.Union[str, str, str], None]] = None


class VacancyWithCount(BaseModel):
    vacancies: typing.List[Vacancy]
    vacancies_count: int


def make_request(
    self: BaseApi,
    __request__: Vacancy,
    exclude_by: str = ...,
    exclude_values: str = ...,
    is_aboard: str = ...,
    max_salary: str = ...,
    min_salary: str = ...,
    search_by: str = ...,
    search_values: str = ...,
    slug: str = ...,
    type: str = ...,
) -> VacancyWithCount:
    body = __request__

    m = ApiRequest(
        method="POST",
        path="/api/v1/vacancy/".format(),
        content_type="application/json",
        body=body,
        headers=self._only_provided({}),
        query_params=self._only_provided(
            {
                "exclude_by": exclude_by,
                "exclude_values": exclude_values,
                "is_aboard": is_aboard,
                "max_salary": max_salary,
                "min_salary": min_salary,
                "search_by": search_by,
                "search_values": search_values,
                "slug": slug,
                "type": type,
            }
        ),
        cookies=self._only_provided({}),
    )
    return self.make_request(
        {
            "200": {
                "application/json": VacancyWithCount,
            },
        },
        m,
    )
