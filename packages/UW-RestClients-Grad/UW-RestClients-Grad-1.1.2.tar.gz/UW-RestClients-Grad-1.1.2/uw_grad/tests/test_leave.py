# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import datetime
from unittest import TestCase
from restclients_core.exceptions import DataFailureException
from uw_grad.leave import get_leave_by_syskey
from uw_grad.util import fdao_grad_override


@fdao_grad_override
class LeaveTest(TestCase):

    def test_get_leave_by_syskey(self):
        requests = get_leave_by_syskey("000083856")

        self.assertEqual(len(requests), 5)
        leave = requests[0]
        self.assertIsNotNone(leave.json_data())
        self.assertEqual(leave.reason,
                         "Dissertation/Thesis research/writing")
        self.assertEqual(leave.submit_date,
                         datetime.datetime(2012, 9, 10, 9, 40, 3, 360000))
        self.assertEqual(leave.status, "paid")
        self.assertTrue(leave.is_status_paid())
        self.assertFalse(leave.is_status_approved())
        self.assertFalse(leave.is_status_denied())
        self.assertFalse(leave.is_status_requested())
        self.assertFalse(leave.is_status_withdrawn())
        self.assertEqual(len(leave.terms), 1)
        self.assertEqual(leave.terms[0].quarter, "autumn")
        self.assertEqual(leave.terms[0].year, 2012)

    def test_error(self):
        self.assertRaises(DataFailureException,
                          get_leave_by_syskey, "000000001")
