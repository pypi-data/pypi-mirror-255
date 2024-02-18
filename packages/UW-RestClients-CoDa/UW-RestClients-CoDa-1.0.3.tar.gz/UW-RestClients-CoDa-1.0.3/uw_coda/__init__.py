# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from restclients_core.exceptions import DataFailureException
from uw_coda.dao import CoDa_DAO
import json

DAO = CoDa_DAO()

API_BASE = "/api/v1/course/{id}/"


def get_resource(section_label, endpoint):
    section_label = format_section_label(section_label)
    url = get_offering_url(section_label) + endpoint

    if _is_secondary(section_label):
        return {}

    response = DAO.getURL(url)

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)
    else:
        return json.loads(response.data)


def get_majors(section_label, num_majors):
    return get_resource(section_label, "majors/{}".format(num_majors))


def get_fail_rate(section_label):
    return get_resource(section_label, "fail_rate")


def get_course_cgpa(section_label):
    return get_resource(section_label, "cgpa")


def get_offering_url(section_label):
    return API_BASE.format(id=section_label)


def format_section_label(section_label):
    return section_label.replace(",", "-").replace("/", "-")


def _is_secondary(section_label):
    parts = section_label.split("-")

    id = parts[len(parts) - 1]

    return len(id) > 1
