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
import uuid
import logging
from Singleton import Singleton

class MockStackEnvironment(Singleton):

    def _singleton_init(self, username, password, tenant, auth_url):
        # This is the only config difference that we currently care about
        # cheat and turn it on or off based on the username
        if username == "nocinder":
            self.cinder = False
        else:
            self.cinder = True
        self.log = logging.getLogger('%s.%s' % (__name__, self.__class__.__name__))
        self.log.debug("MockStackEnvironment is doing a singleton init")
        # Save these just because
        self.username = username
        self.password = password
        self.tenant = tenant
        self.auth_url = auth_url

    def __init__(self, username, password, tenant, auth_url):
        pass

    def is_cinder(self):
        return self.cinder

    def upload_image_to_glance(self, name, local_path=None, location=None, format='raw', min_disk=0, min_ram=0, container_format='bare', is_public=True):
        self.log.debug("Doing mock glance upload")
        self.log.debug("File: (%s) - Name (%s) - Format (%s) - Container (%s)" % (local_path, name, format, container_format) )  
        return uuid.uuid4()

    def upload_volume_to_cinder(self, name, volume_size=None, local_path=None, location=None, format='raw', container_format='bare', is_public=True, keep_image=True):
        self.log.debug("Doing mock glance upload and cinder copy")
        self.log.debug("File: (%s) - Name (%s) - Format (%s) - Container (%s)" % (local_path, name, format, container_format) )
        return ( uuid.uuid4(), uuid.uuid4() )

