# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interfacing with the GradSchool Degree Request API
"""
import logging
import json
from urllib.parse import urlencode
from uw_grad.models import GradLeave, GradTerm
from uw_grad import get_resource, parse_datetime


PREFIX = "/services/students/v1/api/leave"
logger = logging.getLogger(__name__)


def get_leave_by_syskey(system_key):
    url = "{}?{}".format(PREFIX, urlencode([("id", system_key), ]))
    return _process_json(json.loads(get_resource(url)))


def _process_json(data):
    """
    return a list of GradLeave objects.
    """
    requests = []
    for item in data:
        leave = GradLeave()
        leave.reason = item.get('leaveReason')
        leave.submit_date = parse_datetime(item.get('submitDate'))
        if item.get('status') and len(item.get('status')):
            leave.status = item.get('status').lower()

        for quarter in item.get('quarters'):
            term = GradTerm()
            term.quarter = quarter.get('quarter').lower()
            term.year = quarter.get('year')
            leave.terms.append(term)
        requests.append(leave)
    return requests
