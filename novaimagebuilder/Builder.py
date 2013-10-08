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
from StackEnvironment import StackEnvironment
from time import sleep

class Builder(object):
    def __init__(self, osid, install_location=None, install_type=None, install_script= None, install_config={}):
        """
        Builder selects the correct OS object to delegate build activity to.

        @param osid: The shortid for an OS record.
        @param install_location: The location of an ISO or install tree.
        @param install_type: The type of installation (iso or tree)
        @param install_script: A custom install script to be used instead of what OSInfo can generate
        @param install_config: A dict of various info that may be needed for the build.
                                (admin_pw, license_key, arch, disk_size, flavor, storage, name)
        """
        super(Builder, self).__init__()
        self.log = logging.getLogger('%s.%s' % (__name__, self.__class__.__name__))
        self.install_location = install_location
        self.install_type = install_type
        self.install_script = install_script
        self.install_config = install_config
        self.os = OSInfo().os_for_shortid(osid)
        self.os_delegate = self._delegate_for_os(self.os)
        self.env = StackEnvironment()

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
                os_module = __import__("novaimagebuilder." + os_classname, fromlist=[os_classname])
                os_class = getattr(os_module, os_classname)
                #import pdb; pdb.set_trace()
                return os_class(osinfo_dict=self.os,
                                install_type=self.install_type,
                                install_media_location=self.install_location,
                                install_config=self.install_config,
                                install_script=self.install_script)
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

    def wait_for_completion(self):
        """
        Waits for the install_instance to enter SHUTDOWN state then launches a snapshot

        @return: Success or Failure
        """
        # TODO: Timeouts, activity checking
        raw_instance = self.os_delegate.install_instance.instance
        self._wait_for_shutoff(raw_instance)
        # Snapshot with self.install_config['name']
        finished_image_id = raw_instance.create_image(self.install_config['name'])
        self._wait_for_glance_snapshot(finished_image_id)
        self._terminate_instance(raw_instance.id)

    def _wait_for_shutoff(self, instance):
	for i in range(1200):
	    status = self.env.nova.servers.get(instance.id).status
	    if status == "SHUTOFF":
		self.log.debug("Instance (%s) has entered SHUTOFF state" % (instance.id) )
		return instance
	    if i % 10 == 0:
		self.log.debug("Waiting for instance status SHUTOFF - current status (%s): %d/1200" % (status, i))
	    sleep(1)

    def _wait_for_glance_snapshot(self, image_id):
	image = self.env.glance.images.get(image_id)
	self.log.debug("Waiting for glance image id (%s) to become active" % (image_id))
	while True:
	    self.log.debug("Current image status: %s" % (image.status))
	    sleep(2)
	    image = self.env.glance.images.get(image.id)
	    if image.status == "error":
		raise Exception("Image entered error status while waiting for completion")
	    elif image.status == 'active':
		break
        # Remove any direct boot properties if they exist
        properties = image.properties 
	for key in [ 'kernel_id', 'ramdisk_id', 'command_line' ]:
	    if key in properties:
		del properties[key]
	meta = {'properties':properties}
	image.update(**meta)

    def _terminate_instance(self, instance_id):
        nova = self.env.nova
        instance = nova.servers.get(instance_id)
        instance.delete()
	self.log.debug("Waiting for instance id (%s) to be terminated/delete" % (instance_id))
	while True:
	    self.log.debug("Current instance status: %s" % (instance.status))
	    sleep(5)
	    try:
		instance = nova.servers.get(instance_id)
	    except Exception as e:
		self.log.debug("Got exception (%s) assuming deletion complete" % (e))
		break

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
