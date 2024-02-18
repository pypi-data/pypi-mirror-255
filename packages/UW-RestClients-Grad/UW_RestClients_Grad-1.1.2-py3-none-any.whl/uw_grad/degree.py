# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interfacing with the Grad School Degree Request API
"""
import logging
import json
from urllib.parse import urlencode
from uw_grad.models import GradDegree
from uw_grad import get_resource, parse_datetime


PREFIX = "/services/students/v1/api/request"
logger = logging.getLogger(__name__)


def get_degree_by_syskey(system_key, exclude_past_quarter=True):
    params = [
        ("id", system_key),
        ("exclude_past_quarter", "true" if exclude_past_quarter else ""), ]
    url = "{}?{}".format(PREFIX, urlencode(params))
    return _process_json(json.loads(get_resource(url)))


def _process_json(json_data):
    """
    return a list of GradDegree objects.
    """
    requests = []
    for item in json_data:
        degree = GradDegree()
        degree.degree_title = item["degreeTitle"]
        degree.exam_place = item["examPlace"]
        degree.exam_date = parse_datetime(item.get("examDate"))
        degree.req_type = item["requestType"]
        degree.major_full_name = item["majorFullName"]
        degree.submit_date = parse_datetime(item.get("requestSubmitDate"))
        degree.decision_date = parse_datetime(item.get('decisionDate'))
        degree.status = item["status"]
        degree.target_award_year = item["targetAwardYear"]
        if (item.get("targetAwardQuarter") and
                len(item.get("targetAwardQuarter"))):
            degree.target_award_quarter = item["targetAwardQuarter"].lower()

        requests.append(degree)
    return requests
