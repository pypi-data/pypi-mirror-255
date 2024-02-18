from __future__ import annotations

from feedancy.lib.base import BaseApi

from . import api_v1_activitysphere_retrieve
from . import api_v1_activitysphere_create
from . import api_v1_activitysphere_retrieve_2
from . import api_v1_activitysphere_update
from . import api_v1_activitysphere_destroy
from . import api_v1_city_retrieve
from . import api_v1_city_create
from . import api_v1_city_retrieve_2
from . import api_v1_city_update
from . import api_v1_city_destroy
from . import api_v1_company_retrieve
from . import api_v1_company_create
from . import api_v1_company_retrieve_2
from . import api_v1_company_update
from . import api_v1_company_destroy
from . import api_v1_companycity_retrieve
from . import api_v1_companycity_create
from . import api_v1_companycity_retrieve_2
from . import api_v1_companycity_update
from . import api_v1_companycity_destroy
from . import api_v1_contact_retrieve
from . import api_v1_contact_create
from . import api_v1_contact_retrieve_2
from . import api_v1_contact_update
from . import api_v1_contact_destroy
from . import api_v1_country_retrieve
from . import api_v1_country_create
from . import api_v1_country_retrieve_2
from . import api_v1_country_update
from . import api_v1_country_destroy
from . import api_v1_currency_retrieve
from . import api_v1_currency_create
from . import api_v1_currency_retrieve_2
from . import api_v1_currency_update
from . import api_v1_currency_destroy
from . import api_v1_internship_list
from . import api_v1_internship_create
from . import api_v1_internship_retrieve
from . import api_v1_internship_update
from . import api_v1_internship_destroy
from . import api_v1_internshipcontact_retrieve
from . import api_v1_internshipcontact_create
from . import api_v1_internshipcontact_retrieve_2
from . import api_v1_internshipcontact_update
from . import api_v1_internshipcontact_destroy
from . import api_v1_internshipskill_retrieve
from . import api_v1_internshipskill_create
from . import api_v1_internshipskill_retrieve_2
from . import api_v1_internshipskill_update
from . import api_v1_internshipskill_destroy
from . import api_v1_jobmixin_retrieve
from . import api_v1_jobmixin_create
from . import api_v1_jobmixin_retrieve_2
from . import api_v1_jobmixin_update
from . import api_v1_jobmixin_destroy
from . import api_v1_keywords_create
from . import api_v1_keywords_update
from . import api_v1_keywords_destroy
from . import api_v1_region_retrieve
from . import api_v1_region_create
from . import api_v1_region_retrieve_2
from . import api_v1_region_update
from . import api_v1_region_destroy
from . import api_v1_salary_retrieve
from . import api_v1_salary_create
from . import api_v1_salary_retrieve_2
from . import api_v1_salary_update
from . import api_v1_salary_destroy
from . import api_v1_salary_avg_retrieve
from . import api_v1_salary_diagram_retrieve
from . import api_v1_skill_retrieve
from . import api_v1_skill_create
from . import api_v1_skill_retrieve_2
from . import api_v1_skill_update
from . import api_v1_skill_destroy
from . import api_v1_source_retrieve
from . import api_v1_source_create
from . import api_v1_source_retrieve_2
from . import api_v1_source_update
from . import api_v1_source_destroy
from . import api_v1_vacancy_list
from . import api_v1_vacancy_create
from . import api_v1_vacancy_retrieve
from . import api_v1_vacancy_update
from . import api_v1_vacancy_destroy
from . import api_v1_vacancycontact_retrieve
from . import api_v1_vacancycontact_create
from . import api_v1_vacancycontact_retrieve_2
from . import api_v1_vacancycontact_update
from . import api_v1_vacancycontact_destroy
from . import api_v1_vacancyskill_retrieve
from . import api_v1_vacancyskill_create
from . import api_v1_vacancyskill_retrieve_2
from . import api_v1_vacancyskill_update
from . import api_v1_vacancyskill_destroy


class ApiApi(BaseApi):
    api_v1_activitysphere_retrieve = api_v1_activitysphere_retrieve.make_request
    api_v1_activitysphere_create = api_v1_activitysphere_create.make_request
    api_v1_activitysphere_retrieve_2 = api_v1_activitysphere_retrieve_2.make_request
    api_v1_activitysphere_update = api_v1_activitysphere_update.make_request
    api_v1_activitysphere_destroy = api_v1_activitysphere_destroy.make_request
    api_v1_city_retrieve = api_v1_city_retrieve.make_request
    api_v1_city_create = api_v1_city_create.make_request
    api_v1_city_retrieve_2 = api_v1_city_retrieve_2.make_request
    api_v1_city_update = api_v1_city_update.make_request
    api_v1_city_destroy = api_v1_city_destroy.make_request
    api_v1_company_retrieve = api_v1_company_retrieve.make_request
    api_v1_company_create = api_v1_company_create.make_request
    api_v1_company_retrieve_2 = api_v1_company_retrieve_2.make_request
    api_v1_company_update = api_v1_company_update.make_request
    api_v1_company_destroy = api_v1_company_destroy.make_request
    api_v1_companycity_retrieve = api_v1_companycity_retrieve.make_request
    api_v1_companycity_create = api_v1_companycity_create.make_request
    api_v1_companycity_retrieve_2 = api_v1_companycity_retrieve_2.make_request
    api_v1_companycity_update = api_v1_companycity_update.make_request
    api_v1_companycity_destroy = api_v1_companycity_destroy.make_request
    api_v1_contact_retrieve = api_v1_contact_retrieve.make_request
    api_v1_contact_create = api_v1_contact_create.make_request
    api_v1_contact_retrieve_2 = api_v1_contact_retrieve_2.make_request
    api_v1_contact_update = api_v1_contact_update.make_request
    api_v1_contact_destroy = api_v1_contact_destroy.make_request
    api_v1_country_retrieve = api_v1_country_retrieve.make_request
    api_v1_country_create = api_v1_country_create.make_request
    api_v1_country_retrieve_2 = api_v1_country_retrieve_2.make_request
    api_v1_country_update = api_v1_country_update.make_request
    api_v1_country_destroy = api_v1_country_destroy.make_request
    api_v1_currency_retrieve = api_v1_currency_retrieve.make_request
    api_v1_currency_create = api_v1_currency_create.make_request
    api_v1_currency_retrieve_2 = api_v1_currency_retrieve_2.make_request
    api_v1_currency_update = api_v1_currency_update.make_request
    api_v1_currency_destroy = api_v1_currency_destroy.make_request
    api_v1_internship_list = api_v1_internship_list.make_request
    api_v1_internship_create = api_v1_internship_create.make_request
    api_v1_internship_retrieve = api_v1_internship_retrieve.make_request
    api_v1_internship_update = api_v1_internship_update.make_request
    api_v1_internship_destroy = api_v1_internship_destroy.make_request
    api_v1_internshipcontact_retrieve = api_v1_internshipcontact_retrieve.make_request
    api_v1_internshipcontact_create = api_v1_internshipcontact_create.make_request
    api_v1_internshipcontact_retrieve_2 = (
        api_v1_internshipcontact_retrieve_2.make_request
    )
    api_v1_internshipcontact_update = api_v1_internshipcontact_update.make_request
    api_v1_internshipcontact_destroy = api_v1_internshipcontact_destroy.make_request
    api_v1_internshipskill_retrieve = api_v1_internshipskill_retrieve.make_request
    api_v1_internshipskill_create = api_v1_internshipskill_create.make_request
    api_v1_internshipskill_retrieve_2 = api_v1_internshipskill_retrieve_2.make_request
    api_v1_internshipskill_update = api_v1_internshipskill_update.make_request
    api_v1_internshipskill_destroy = api_v1_internshipskill_destroy.make_request
    api_v1_jobmixin_retrieve = api_v1_jobmixin_retrieve.make_request
    api_v1_jobmixin_create = api_v1_jobmixin_create.make_request
    api_v1_jobmixin_retrieve_2 = api_v1_jobmixin_retrieve_2.make_request
    api_v1_jobmixin_update = api_v1_jobmixin_update.make_request
    api_v1_jobmixin_destroy = api_v1_jobmixin_destroy.make_request
    api_v1_keywords_create = api_v1_keywords_create.make_request
    api_v1_keywords_update = api_v1_keywords_update.make_request
    api_v1_keywords_destroy = api_v1_keywords_destroy.make_request
    api_v1_region_retrieve = api_v1_region_retrieve.make_request
    api_v1_region_create = api_v1_region_create.make_request
    api_v1_region_retrieve_2 = api_v1_region_retrieve_2.make_request
    api_v1_region_update = api_v1_region_update.make_request
    api_v1_region_destroy = api_v1_region_destroy.make_request
    api_v1_salary_retrieve = api_v1_salary_retrieve.make_request
    api_v1_salary_create = api_v1_salary_create.make_request
    api_v1_salary_retrieve_2 = api_v1_salary_retrieve_2.make_request
    api_v1_salary_update = api_v1_salary_update.make_request
    api_v1_salary_destroy = api_v1_salary_destroy.make_request
    api_v1_salary_avg_retrieve = api_v1_salary_avg_retrieve.make_request
    api_v1_salary_diagram_retrieve = api_v1_salary_diagram_retrieve.make_request
    api_v1_skill_retrieve = api_v1_skill_retrieve.make_request
    api_v1_skill_create = api_v1_skill_create.make_request
    api_v1_skill_retrieve_2 = api_v1_skill_retrieve_2.make_request
    api_v1_skill_update = api_v1_skill_update.make_request
    api_v1_skill_destroy = api_v1_skill_destroy.make_request
    api_v1_source_retrieve = api_v1_source_retrieve.make_request
    api_v1_source_create = api_v1_source_create.make_request
    api_v1_source_retrieve_2 = api_v1_source_retrieve_2.make_request
    api_v1_source_update = api_v1_source_update.make_request
    api_v1_source_destroy = api_v1_source_destroy.make_request
    api_v1_vacancy_list = api_v1_vacancy_list.make_request
    api_v1_vacancy_create = api_v1_vacancy_create.make_request
    api_v1_vacancy_retrieve = api_v1_vacancy_retrieve.make_request
    api_v1_vacancy_update = api_v1_vacancy_update.make_request
    api_v1_vacancy_destroy = api_v1_vacancy_destroy.make_request
    api_v1_vacancycontact_retrieve = api_v1_vacancycontact_retrieve.make_request
    api_v1_vacancycontact_create = api_v1_vacancycontact_create.make_request
    api_v1_vacancycontact_retrieve_2 = api_v1_vacancycontact_retrieve_2.make_request
    api_v1_vacancycontact_update = api_v1_vacancycontact_update.make_request
    api_v1_vacancycontact_destroy = api_v1_vacancycontact_destroy.make_request
    api_v1_vacancyskill_retrieve = api_v1_vacancyskill_retrieve.make_request
    api_v1_vacancyskill_create = api_v1_vacancyskill_create.make_request
    api_v1_vacancyskill_retrieve_2 = api_v1_vacancyskill_retrieve_2.make_request
    api_v1_vacancyskill_update = api_v1_vacancyskill_update.make_request
    api_v1_vacancyskill_destroy = api_v1_vacancyskill_destroy.make_request
