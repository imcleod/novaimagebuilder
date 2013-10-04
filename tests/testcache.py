#!/usr/bin/python
import sys
sys.path.append("../")
from MockStackEnvironment import MockStackEnvironment as StackEnvironment
from CacheManager import CacheManager
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s thread(%(threadName)s) Message: %(message)s')

class MockOSPlugin(object):
    
    def __init__(self, os_ver_arch = "fedora19-x86_64", wants_iso = True ):
        self.nameverarch = os_ver_arch
        self.wantscdrom = wants_iso

    def os_ver_arch(self):
        return self.nameverarch

    def wants_iso(self):
        return self.wants_iso

print "---- the following should do a glance and cinder upload"

mosp = MockOSPlugin(os_ver_arch = "fedora18-x86_64", wants_iso = False)
mse = StackEnvironment("username","password","tenant","auth_url")
cm = CacheManager(mse)

cm.retrieve_and_cache_object("install-iso", mosp, "http://repos.fedorapeople.org/repos/aeolus/imagefactory/testing/repos/rhel/imagefactory.repo",
                             True)
