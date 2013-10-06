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
import os
from NovaInstance import NovaInstance

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

    def upload_image_to_glance(self, name, local_path=None, location=None, format='raw', min_disk=0, min_ram=0, container_format='bare', is_public=True, properties={}):
        image_meta = {'container_format': container_format, 'disk_format': format, 'is_public': is_public, 'min_disk': min_disk, 'min_ram': min_ram, 'name': name, 'properties': properties}
        try:
            image_meta['data'] = open(local_path, "r")
        except Exception, e:
            if location:
                image_meta['location'] = location
            else:
                raise e
        
        image = self.glance.images.create(name=name)
        print 'Started uploading to Glance'
        image.update(**image_meta)
        while image.status != 'active':
            image = self.glance.images.get(image.id)
            if image.status == 'error':
                raise Exception('Error uploading image to Glance.')
            sleep(1)
        print 'Finished uploading to Glance'
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

    def delete_image(self, image_id):
        self.glance.images.get(image_id).delete()

    def delete_volume(self, volume_id):
        self.cinder.volumes.get(volume_id).delete()

    def _migrate_from_glance_to_cinder(self, image_id, volume_size):
        image = self.glance.images.get(image_id)
        if not volume_size:
        # Gigabytes rounded up
            volume_size = int(image.size/(1024*1024*1024)+1)

        print 'Started copying to Cinder'
        volume = self.cinder.volumes.create(volume_size, display_name=image.name, imageRef=image.id)
        while volume.status != 'available':
            volume = self.cinder.volumes.get(volume.id)
            if volume.status == 'error':
                volume.delete()
                raise Exception('Error occured copying glance image %s to volume %s' % (image_id, volume.id))
            sleep(1)
        print 'Finished copying to Cinder'
        return volume.id

    def get_volume_status(self, volume_id):
        volume = self.cinder.volumes.get(volume.id)
        return volume.status
    
    def get_image_status(self, image_id):
        image = self.glance.images.get(image_id)
        return image.status

    def _create_blank_image(self, size):
        rc = os.system("qemu-img create -f qcow2 blank_image.tmp %dG" % size)
        if rc == 0:
            return
        else:
            raise Exception("Unable to create blank image")


    def _remove_blank_image(self):
        rc = os.system("rm blank_image.tmp")
        if rc == 0:
            return
        else:
            raise Exception("Unable to create blank image")

    def launch_instance(self, root_disk=None, install_iso=None, secondary_iso=None, floppy=None, aki=None, ari=None, cmdline=None, userdata=None):
        if root_disk:
            #if root disk needs to be created
            if root_disk[0] == 'blank':
                root_disk_size = root_disk[1]
                #Create a blank qcow2 image and uploads it
                self._create_blank_image(root_disk_size)
                if aki and ari and cmdline:
                    root_disk_properties = {'kernel_id': aki, 'ramdisk_id': ari, 'command_line': cmdline}
                else:
                    root_disk_properties = {}
                root_disk_image_id = self.upload_image_to_glance('blank %dG disk' % root_disk_size, local_path='./blank_image.tmp', format='qcow2', properties=root_disk_properties)
                self._remove_blank_image()
            elif root_disk[0] == 'glance':
                root_disk_image_id = root_disk[1]

        #blank root disk with ISO, ISO2 and Floppy - Windows
        if install_iso and secondary_iso and floppy:
            if install_iso[0] == 'cinder':
                install_iso_id = install_iso[1]
            else:
                install_iso_id = self.create_volume_from_image(install_iso[1])

            if secondary_iso[0] == 'cinder':
                secondary_iso_id = secondary_iso[1]
            else:
                secondary_iso_id = self.create_volume_from_image(secondary_iso[1])

            if floppy[0] == 'cinder':
                floppy_id = floppy[1]
            else:
                floppy_id = self.create_volume_from_image(floppy[1])
            instance = self._launch_windows_install(root_disk_image_id, install_iso_id, secondary_iso_id, floppy_id)
            return NovaInstance(instance, self)

        #blank root disk with aki, ari and cmdline. install iso is optional.
        if aki and ari and cmdline and userdata:
            instance_id = self._launch_direct_boot(root_disk_image_id, userdata, install_iso=install_iso)
            return NovaInstance(instance_id, self)

    def _launch_direct_boot(self, root_disk, userdata, install_iso=None):
        image = self.glance.images.get(root_disk)
        if install_iso:
            #assume that install iso is already a cinder volume
            block_device_mapping_v2 = [
                     {"source_type": "volume",
                     "destination_type": "volume",
                     "uuid": install_cdrom,
                     "boot_index": "1",
                     "device_type": "cdrom",
                     "disk_bus": "ide",
                    },
                    ]
        else:
           #must be a network install
           block_device_mapping_v2 = None
        instance = self.nova.servers.create("direct-boot-linux", image, "2", block_device_mapping_v2=block_device_mapping_v2, userdata=userdata)
        return instance
    
    def _launch_windows_install(self, root_disk, install_cdrom, drivers_cdrom, autounattend_floppy):

        block_device_mapping_v2 = [
                     {"source_type": "volume",
                     "destination_type": "volume",
                     "uuid": install_cdrom,
                     "boot_index": "1",
                     "device_type": "cdrom",
                     "disk_bus": "ide",
                    },
                    {"source_type": "volume",
                     "destination_type": "volume",
                     "uuid": drivers_cdrom,
                     "boot_index": "3",
                     "device_type": "cdrom",
                     "disk_bus": "ide",
                    },
                    {"source_type": "volume",
                     "destination_type": "volume",
                     "uuid": autounattend_floppy,
                     "boot_index": "2",
                     "device_type": "floppy",
                    },
                    ]

        try:
            image = self.glance.images.get(root_disk)
            instance = self.nova.servers.create("windows-volume-backed", image, "2", meta={}, block_device_mapping_v2 = block_device_mapping_v2)
            return instance
        except Exception, e:
            print "Error has occured: %s" % e.message

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
        return True

