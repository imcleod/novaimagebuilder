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
from BaseOS import BaseOS

class RedHatOS(BaseOS):

    def __init__(self, osinfo_dict, install_type, install_media_location, install_config, install_script = None):
        super(RedHatOS, self).__init__(osinfo_dict, install_type, install_media_location, install_config, install_script)

        #TODO: Check for direct boot - for now we are using environments
        #      where we know it is present
        #if not self.env.is_direct_boot():
        #    raise Exception("Direct Boot feature required - Installs using syslinux stub not yet implemented")

        if install_type == "iso" and not self.env.is_cdrom():
            raise Exceptino("ISO installs require a Nova environment that can support CDROM block device mapping")

    def prepare_install_instance(self):
        """ Method to prepare all necessary local and remote images for an install
            This method may require significant local disk or CPU resource
        """
        if self.install_type == "iso":
            iso_locations = self.cache.retrieve_and_cache_object("install-iso", self, self.install_media_location, True)
            self.iso_volume = iso_locations['cinder']
            self.iso_aki = self.cache.retrieve_and_cache_object("install-iso-kernel", self, None, True)['glance']
            self.iso_ari = self.cache.retrieve_and_cache_object("install-iso-initrd", self, None, True)['glance']            
            self.log.debug ("Prepared cinder iso (%s), aki (%s) and ari (%s) for install instance" %
                            ( self.iso_volume, self.iso_aki, self.iso_ari ) )    

    def start_install_instance(self):
        if self.install_type == "iso":
            self.log.debug("Launching direct boot ISO install instance")
            self.install_instance = self.env.launch_instance(root_disk=('blank', 10), install_iso=('cinder', self.iso_volume),
                                                                        aki=self.iso_aki, ari=self.iso_ari, 
                                                                        cmdline="ks=http://169.254.169.254/latest/user-data", 
                                                                        userdata=self.install_script)

    def update_status(self):
        return "RUNNING"

    def wants_iso_content(self):
        return True

    def iso_content_dict(self):
        return { "install-iso-kernel": "/images/pxeboot/vmlinuz",
                 "install-iso-initrd": "/images/pxeboot/initrd.img" }

    def url_content_dict(self):
        return { "install-url-kernel": "/images/pxeboot/vmlinuz",
                 "install-url-initrd": "/images/pxeboot/initrd.img" }

    def abort(self):
        pass

    def cleanup(self):
        pass
