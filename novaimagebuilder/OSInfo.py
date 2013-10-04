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

import logging
from gi.repository import Libosinfo as osinfo
from gi.repository import Gio


class OSInfo(object):
    def __init__(self, path='/usr/share/libosinfo/db'):
        super(OSInfo, self).__init__()
        self.log = logging.getLogger('%s.%s' % (__name__, self.__class__.__name__))
        loader = osinfo.Loader()
        loader.process_path(path)
        self.db = loader.get_db()

    def os_for_iso(self, iso):
        """
        Given an install ISO, get information about the OS.

        @param iso URL of an install iso

        @return dict with keys:
            name
            version
            distro
            family
            shortid
            id
            media_list
            tree_list
            minimum_resources
            recommended_resources
        """
        pass

    def os_for_tree(self, tree):
        """
        Given an install tree, get information about the OS.

        @param tree URL of an install tree

        @return dict with keys:
            name
            version
            distro
            family
            shortid
            id
            media_list
            tree_list
            minimum_resources
            recommended_resources
        """
        pass

    def install_script(self, osid, configuration, profile='jeos'):
        """
        Get an install script for a given OS.

        @param osid Either the shortid or id for an OS (str)

        @param configuration A dict of install script customizations with the following keys:
            admin_password (required)
            license (optional, default: None)
            target_disk (optional, default: None)
            script_disk (optional, default: None)
            preinstall_disk (optional, default: None)
            postinstall_disk (optional, default: None)
            signed_drivers (optional, default: True)
            keyboard (optional, default: 'en_US')
            language (optional, default: 'en_US')
            timezone (optional, default: 'America/New_York')

        @param profile The profile of the install. (str) 'jeos', 'desktop', etc

        @return install script as a str
        """
        pass

    def os_ids(self, distros=None):
        """
        List the operating systems available from libosinfo.

        @param distros A dict with keys being distro names and the values being the lowest version to list.
            Ex. {'fedora': 17, 'rhel': 5, 'ubuntu':12, 'win':6}

        @return A dict with keys being OS shortid and values being OS name
        """
        os_dict = {}
        for os in self.db.get_os_list().get_elements():
            if distros:
                distro = os.get_distro()
                version = int(os.get_version().split('.')[0])  # Just compare major versions, ie 2 instead of 2.2.8
                for a_distro in distros:
                    if a_distro == distro and version >= distros[a_distro]:
                        os_dict[os.get_short_id()] = os.get_name()
            else:
               os_dict[os.get_short_id()] = os.get_name()

        return os_dict