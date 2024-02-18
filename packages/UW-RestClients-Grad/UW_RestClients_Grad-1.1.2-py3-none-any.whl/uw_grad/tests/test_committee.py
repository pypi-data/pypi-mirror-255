# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import datetime
from unittest import TestCase
from restclients_core.exceptions import DataFailureException
from uw_grad.committee import get_committee_by_syskey
from uw_grad.util import fdao_grad_override


@fdao_grad_override
class CommitteeTest(TestCase):

    def test_get_committee_by_syskey(self):
        requests = get_committee_by_syskey("000083856")

        self.assertEqual(len(requests), 3)

        committee = requests[0]
        self.assertIsNotNone(committee.json_data())
        self.assertEqual(committee.committee_type,
                         "Advisor")
        self.assertEqual(committee.status, "active")
        self.assertEqual(committee.dept, "Anthropology")
        self.assertEqual(committee.degree_title, None)
        self.assertEqual(committee.degree_type,
                         "MASTER OF PUBLIC HEALTH (EPIDEMIOLOGY)")
        self.assertEqual(committee.major_full_name, "ANTH")
        self.assertEqual(committee.start_date,
                         datetime.datetime(2012, 12, 7, 8, 26, 14, 770000))
        self.assertEqual(len(committee.members), 1)

        committee = requests[1]
        self.assertEqual(committee.committee_type,
                         "Master's Committee")
        members = committee.members
        self.assertEqual(len(members), 3)
        self.assertEqual(members[0].first_name, "Nina L.")
        self.assertEqual(members[0].last_name, "Patrick")
        self.assertTrue(members[0].is_type_chair())
        self.assertTrue(members[0].is_reading_committee_chair())
        self.assertEqual(members[0].dept, "Epidemiology - Public Health")
        self.assertEqual(members[0].email, "nnn@u.washington.edu")
        self.assertEqual(members[0].status, "active")

        self.assertFalse(members[1].is_type_chair())
        self.assertFalse(members[1].is_reading_committee_chair())
        self.assertTrue(members[1].is_type_member())
        self.assertTrue(members[1].is_reading_committee_member())
        self.assertTrue(members[2].is_type_gsr())
        self.assertTrue(members[2].is_reading_committee_member())

        json_data = committee.json_data()
        self.assertEqual(len(json_data["members"]), 3)
        member_json = json_data["members"][0]
        self.assertEqual(member_json["member_type"], "Chair")
        self.assertEqual(member_json["reading_type"],
                         "Reading Committee Chair")
        member_json = json_data["members"][1]
        self.assertEqual(member_json["member_type"], "GSR")
        member_json = json_data["members"][2]
        self.assertEqual(member_json["member_type"], None)

        committee = requests[2]
        self.assertEqual(committee.committee_type,
                         "Doctoral Supervisory Committee")
        members = committee.members
        self.assertEqual(len(members), 4)
        self.assertFalse(members[0].__eq__(members[1]))
        self.assertFalse(members[0] == members[1])
        self.assertTrue(members[0].__ne__(members[1]))
        self.assertTrue(members[0] != members[1])
        json_data = committee.json_data()
        self.assertEqual(len(json_data["members"]), 4)
        member_json = json_data["members"][0]
        self.assertEqual(member_json["member_type"],
                         "Chair")
        self.assertEqual(member_json["last_name"],
                         "Duncan")
        member_json = json_data["members"][1]
        self.assertEqual(member_json["member_type"],
                         "Chair")
        self.assertEqual(member_json["last_name"],
                         "Goodman")
        member_json = json_data["members"][2]
        self.assertEqual(member_json["member_type"],
                         "GSR")
        member_json = json_data["members"][3]
        self.assertEqual(member_json["member_type"],
                         None)

    def test_error(self):
        # Not found syskey
        self.assertRaises(DataFailureException,
                          get_committee_by_syskey, "0000000001")

        # Not found status param
        self.assertRaises(DataFailureException,
                          get_committee_by_syskey, "000083856", status="all")
