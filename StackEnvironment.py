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

from keystoneclient.v2_0 import client as keystone_client
from novaclient.v1_1 import client as nova_client
from glanceclient import client as glance_client
from cinderclient import client as cinder_client
from Singleton import Singleton
from time import sleep
from novaclient.v1_1.contrib.list_extensions import ListExtManager
import thread

class StackEnvironment(Singleton):

    def _singleton_init(self, username, password, tenant, auth_url):
        super(StackEnvironment, self)._singleton_init()
        
        try:
            self.keystone = keystone_client.Client(username=username, password=password, tenant_name=tenant, auth_url=auth_url)
            self.keystone.authenticate()
        except Exception, e:
            raise Exception('Error authenticating with keystone. Original exception: %s' % e.message)
        try:
            self.nova = nova_client.Client(username, password, tenant, auth_url=auth_url, insecure=True)
        except Exception, e:
            raise Exception('Error connecting to Nova.  Nova is required for building images. Original exception: %s' % e.message)
        try:
            glance_url = self.keystone.service_catalog.get_endpoints()['image'][0]['adminURL']
            self.glance = glance_client.Client('1', endpoint=glance_url, token=self.keystone.auth_token)
        except Exception, e:
            raise Exception('Error connecting to glance. Glance is required for building images. Original exception: %s' % e.message)
        
        try:
            self.cinder = cinder_client.Client('1', username, password, tenant, auth_url)
        except:
            self.cinder = None


    def __init__(self, username, password, tenant, auth_url):
        pass

    @property
    def keystone_server(self):
        return self.keystone

    @property
    def glance_server(self):
        return self.glance

    @property
    def cinder_server(self):
        return self.cinder

    def upload_image_to_glance(self, name, local_path=None, location=None, format='raw', min_disk=0, min_ram=0, container_format='bare', is_public=True):
        image_meta = {'container_format': container_format, 'disk_format': format, 'is_public': is_public, 'min_disk': min_disk, 'min_ram': min_ram, 'name': name}
        try:
            image_meta['data'] = open(local_path, "r")
        except Exception, e:
            if location:
                image_meta['location'] = location
            else:
                raise e
        
        image = self.glance.images.create(name=name)
        image.update(**image_meta)
        return image.id

    def upload_volume_to_cinder(self, name, volume_size=None, local_path=None, location=None, format='raw', container_format='bare', is_public=True, keep_image=True):
        image_id = self.upload_image_to_glance(name, local_path=local_path, location=location, format=format, is_public=is_public)
        volume_id = self._migrate_from_glance_to_cinder(image_id, volume_size)
        if not keep_image:
            #TODO: spawn a thread to delete image after volume is created
            return volume_id
        return (image_id, volume_id)
        

    def create_volume_from_image(self, image_id, volume_size=None):
        return self._migrate_from_glance_to_cinder(image_id, volume_size)

    def _migrate_from_glance_to_cinder(self, image_id, volume_size):
        image = self.glance.images.get(image_id)
        if not volume_size:
        # Gigabytes rounded up
            volume_size = int(image.size/(1024*1024*1024)+1)

        print "Starting asyncronous copying to Cinder"
        volume = self.cinder.volumes.create(volume_size, display_name=image.name, imageRef=image.id)
        return volume.id

    def get_volume_status(self, volume_id):
        volume = self.cinder.volumes.get(volume.id)
        return volume.status
    
    def get_image_status(self, image_id):
        image = self.glance.images.get(image_id)
        return image.status

    def is_cinder(self):
        if not self.cinder:
            return False
        else:
            return True

    def is_cdrom(self):
        nova_extension_manager = ListExtManager(self.nova)
        for ext in nova_extension_manager.show_all():
            if ext.name == "VolumeAttachmentUpdate" and ext.is_loaded():
                return True
        return False

    def is_floppy(self):
        #TODO: check if floppy is available.  
        pass
 
