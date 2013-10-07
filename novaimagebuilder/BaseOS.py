# encoding: utf-8

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
from CacheManager import CacheManager
from StackEnvironment import StackEnvironment
import inspect

class BaseOS(object):

    def __init__(self, osinfo_dict, install_type, install_media_location, install_script = None):
        self.env = StackEnvironment()
        self.cache = CacheManager()
        self.osinfo_dict = osinfo_dict
        self.install_type = install_type
        self.install_media_location = install_media_location
        self.install_script = install_script
        # Subclasses can pull in the above and then do OS specific tasks to fill in missing
        # information and determine if the resulting install is possible

    def prepare_install_instance(self):
        raise NotImplementedError("Function (%s) not implemented" % (inspect.stack()[0][3]))

    def start_install_instance(self):
        raise NotImplementedError("Function (%s) not implemented" % (inspect.stack()[0][3]))

    def update_status(self):
        """ returns:
              INPROGRESS
              FAILED
              COMPLETE
        """
        raise NotImplementedError("Function (%s) not implemented" % (inspect.stack()[0][3]))

    def wants_iso_content(self):
        raise NotImplementedError("Function (%s) not implemented" % (inspect.stack()[0][3]))

    def iso_content_dict(self):
        raise NotImplementedError("Function (%s) not implemented" % (inspect.stack()[0][3]))

    def url_content_dict(self):
        raise NotImplementedError("Function (%s) not implemented" % (inspect.stack()[0][3]))

    def abort(self):
        raise NotImplementedError("Function (%s) not implemented" % (inspect.stack()[0][3]))

    def cleanup(self):
        raise NotImplementedError("Function (%s) not implemented" % (inspect.stack()[0][3]))
