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


class BaseOS(object):

    def __init__(self, stack_env, osinfo_dict, arch, install_type, install_media_location, install_script = None):
        # stack_env - The OpenStackEnvironment instance
        # 
        self.env = stack_env
        # TODO: Make this a constructor argument?
        self.cache = CacheManager(self.env)
        self.install_script = install_script
        self.os_name = os_name
        self.os_version = os_version
        self.arch = arch
        self.install_type = install_type
        # At this point we have everything all known OSes need to determine the type of install
        # environment and the work needed in the following action methods

        # For example with Fedora/RHEL Linux the logic is
        # If URL install
        # Either way, the prep is to retrieve the kernel and ramdisk        
        # If URL install and no direct boot:
        # prep stub image, which should be removed at cleanup
        # If URL install and direct boot:
        # prep blank image 
        # If CDROM install and cdrom and direct boot
        #   retrieve cdrom, extract kernel and ramdisk, prep blank disk
        # else if not direct boot
        #   prep stub disk instead of blank disk
        # 
        # If URL and direct boot
        #   do direct boot URL install with blank disk
        # else
        #   do direct boot URL install with syslinux stub disk
        # If CDROM and direct boot
        #   do direct boot CDROM install with blank disk
        # else
        #   do direct boot CDROM install with stub disk
        # All of the above use user-data

        # With Windows the logic is
        # Only CDROM install
        # Must have is_cdrom
        # Retrieve CDROM, assert that driver ISO is present, creat and upload stub floppy
        # create and upload blank disk
        #  blank disk should be removed
        #  stub floppy should be something removed
        # Boot with blank, boot iso, driver iso and floppy
        

        # With ubuntu the logic should be nearly identical to Fedora/RHEL


    def prepare_install_instance(self):
        if self.install_type == "iso":
            if self.env.is_cdrom():
                self.cache.retrieve_and_cache_object("install-iso", self, install_media_location, True)
            else:
                raise Exception("MockOS requires real cdrom mapping of ISOs to install - current environment does not support")
        

    def start_install_instance(self):
        pass

    def update_status(self):
        """ returns:
              INPROGRESS
              FAILED
              COMPLETE
        """
        pass

    def wants_iso_content(self):
        pass

    def iso_content_dict(self):
        pass

    def url_content_dict(self):
        pass

    def abort(self):
        pass

    def cleanup(self):
        pass

# low effort/low imact status check
wants_iso_content()
# True if plugin wants a chance to extract content from
# iso before it is pushed to glance/cinder
iso_content_dict()
# keys - paths to extract from ISO
# values - resource types to be used in cache_manager
#  e.g. 
url_content_dict()
# same as above only for url based install
abort()
cleanup()


** OS plugin (Windows, Feodra/RHEL)
* properties
os_name
os_version
os_arch
install_type (url or iso)
suggested_install_timeout()
All explicit and derived input from the CLI entry point
* constructor
# Should be passed the stackenvironment and may fail if the
# install type is incompatible with the environment
# For example, if we cannot map a CDROM, we cannot install windows
* methoids
prepare_install_instance()
# This may require local resource
# prepares stub image or blank image as needed
# prepares one-time use floppy image
# may prepare multi-use drivers ISO
start_install_instance()
# The actual starting should use StackEnvironment
# allowing plugin to be somewhat abstracted in terms
# of the environment it is creating
# this is low-effort
update_status()
# low effort/low imact status check
wants_iso_content()
# True if plugin wants a chance to extract content from
# iso before it is pushed to glance/cinder
iso_content_dict()
# keys - paths to extract from ISO
# values - resource types to be used in cache_manager
#  e.g. 
url_content_dict()
# same as above only for url based install
abort()
cleanup()

