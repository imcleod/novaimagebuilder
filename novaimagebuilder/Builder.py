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
from OSInfo import OSInfo


class Builder(object):
    def __init__(self, osid, install_location=None, install_type=None, install_script= None, name=None):
        """
        Builder selects the correct OS object to delegate build activity to.

        @param osid: The shortid for an OS record.
        @param install_location: The location of an ISO or install tree.
        @param install_type: The type of installation (iso or tree)
        @param install_script: A custom install script to be used instead of what OSInfo can generate
        @param name: A name by which to refer to the built image
        """
        super(Builder, self).__init__()
        self.log = logging.getLogger('%s.%s' % (__name__, self.__class__.__name__))
        self.install_location = install_location
        self.install_type = install_type
        self.install_script = install_script
        self.name = name
        self.os = OSInfo().os_for_shortid(osid)
        self.os_delegate = self._delegate_for_os(self.os)

    def _delegate_for_os(self, os):
        """
        Select and instantiate the correct OS class for build delegation.

        @param os: The dictionary of OS info for a give OS shortid

        @return: An instance of an OS class that will control a VM for the image installation
        """
        # TODO: Change the way we select what class to instantiate to something that we do not have to touch
        # every time we add another OS class
        os_classes = {'fedora': 'RedHatOS', 'rhel': 'RedHatOS', 'windows': 'WindowsOS', 'ubuntu': 'UbuntuOS'}
        os_classname = os_classes.get(os['distro'])

        if os_classname:
            try:
                os_class = __import__(os_classname, fromlist=[os_classname])
                return os_class()
            except ImportError as e:
                self.log.exception(e)
                return None
        else:
            return None

    def run(self):
        """
        Starts the installation of an OS in an image via the appropriate OS class

        @return: Status of the installation.
        """
        self.os_delegate.prepare_install_instance()
        self.os_delegate.start_install_instance()
        return self.os_delegate.update_status()

    def abort(self):
        """
        Aborts the installation of an OS in an image.

        @return: Status of the installation.
        """
        self.os_delegate.abort()
        self.os_delegate.cleanup()
        return self.os_delegate.update_status()

    def status(self):
        """
        Returns the status of the installation.

        @return: Status of the installation.
        """
        # TODO: replace this with a background thread that watches the status and cleans up as needed.
        status = self.os_delegate.update_status()
        if status in ('COMPLETE', 'FAILED'):
            self.os_delegate.cleanup()
        return status