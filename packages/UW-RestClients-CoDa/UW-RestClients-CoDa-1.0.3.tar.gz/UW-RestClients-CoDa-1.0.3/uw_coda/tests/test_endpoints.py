# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase

import uw_coda

POL_S_LABEL = "2014-winter-POL%20S-201-A"
POL_S_AA_LABEL = "2014-winter-POL%20S-201-AA"


class TestEndpoints(TestCase):

    def test_fail_rate(self):
        fail_rate = uw_coda.get_fail_rate(POL_S_LABEL)
        self.assertEqual(fail_rate['failure_rate'], 0.03790613718411552)

    def test_majors(self):
        majors = uw_coda.get_majors(POL_S_LABEL, 2)['current_student_majors']
        self.assertEqual(len(majors), 2)
        self.assertEqual(majors[0]['major'], 'PRE MAJOR (A&S)')

    def test_cgpa(self):
        fail_rate = uw_coda.get_course_cgpa(POL_S_LABEL)
        self.assertEqual(fail_rate['current_median'], 3.4)

    def test_secondary(self):

        fail_rate = uw_coda.get_course_cgpa(POL_S_AA_LABEL)
        self.assertEquals(fail_rate, {})
