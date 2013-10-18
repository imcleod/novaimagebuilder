# coding=utf-8

#   Copyright 2013 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from unittest import TestCase
from novaimagebuilder.OSInfo import OSInfo


class TestOSInfo(TestCase):
    def setUp(self):
        self.osinfo = OSInfo()

    def test_os_id_for_shortid(self):
        os_list = self.osinfo.db.get_os_list().get_elements()
        for os in os_list:
            self.assertEqual(self.osinfo.os_id_for_shortid(os.get_short_id()), os.get_id())

    def test_os_for_shortid(self):
        os = self.osinfo.os_for_shortid('fedora18')
        expected_keys = {'name': str, 'version': str, 'distro': str, 'family': str, 'shortid': str, 'id': str,
                         'media_list': list, 'tree_list': list, 'minimum_resources': list,
                         'recommended_resources': list}

        self.assertIsNotNone(os)
        self.assertIsInstance(os, dict)
        # check that the correct items are in the dict (as defined in OSInfo)
        # and that the values are the correct type
        for key in expected_keys.keys():
            self.assertIn(key, os)
            self.assertIsInstance(os[key], expected_keys[key])

    def test_os_for_iso(self):
        self.fail()

    def test_os_for_tree(self):
        self.fail()

    def test_install_script(self):
        self.fail()

    def test_os_ids(self):
        all_ids = self.osinfo.os_ids()
        fedora_ids = self.osinfo.os_ids({'fedora': 17})

        self.assertIsNotNone(all_ids)
        self.assertIsNotNone(fedora_ids)
        self.assertIsInstance(all_ids, dict)
        self.assertIsInstance(fedora_ids, dict)
        self.assertLess(len(fedora_ids), len(all_ids))