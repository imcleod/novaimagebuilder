# encoding: utf-8

#   Copyright 2012 Red Hat, Inc.
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
import json
import pymongo
from bson.objectid import ObjectId

DB_NAME = "buildbuilder_db"
COLLECTION_NAME = "buildbuilder_collection"


class MongoPersistentBuildManager(object):
    """ TODO: Docstring for PersistentBuildManager  """

    def __init__(self):
        self.log = logging.getLogger('%s.%s' % (__name__, self.__class__.__name__))
        self.con = pymongo.Connection()
        self.db = self.con[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]

    def build_with_id(self, build_id):
        """
        TODO: Docstring for build_with_id

        @param build_id TODO 

        @return TODO
        """
        try:
            build = self._builds_from_query( { "_id" : ObjectId(build_id )} )
        except Exception as e:
            self.log.debug('Exception caught: %s' % e)
            return None
        
        return build

    def add_build(self, build):
        """
        Add a PersistentBuild-type object to this PersistenBuildManager
        This should only be called with an build that has not yet been added to the store.
        To retrieve a previously persisted build use build_with_id() or build_query()

        @param build TODO 

        @return TODO
        """
        if '_id' in build:
            metadata = self.collection.find_one( { "_id": build['_id'] } )
            if metadata:
                raise Exception("Image %s already managed, use build_with_id() and save_build()" % (build.identifier))
        return self._save_build(build)

    def save_build(self, build):
        """
        TODO: Docstring for save_build

        @param build TODO

        @return TODO
        """
        build_id = str(build.identifier)
        metadata = self._from_mongo_meta(self.collection.find_one( { "_id": build_id } ))
        if not metadata:
            raise Exception('Image %s not managed, use "add_build()" first.' % build_id)
        self._save_build(build)

    def _save_build(self, build):
        try:
            build = self.collection.insert(build)
            self.log.debug("Saved metadata for build (%s)" % (build))
            return build.__str__()
        except Exception as e:
            self.log.debug('Exception caught: %s' % e)
            raise Exception('Unable to save build metadata: %s' % e)

    def delete_build_with_id(self, build_id):
        """
        TODO: Docstring for delete_build_with_id

        @param build_id TODO 

        @return TODO
        """
        try:
            self.collection.remove(build_id)
        except Exception as e:
            self.log.warn('Unable to remove mongo record: %s' % e)

    def _builds_from_query(self, query):
        mongo_cursor = self.collection.find(query)
        import pdb;pdb.set_trace()
        builds = self._builds_from_mongo_cursor(mongo_cursor) 
        return builds

    def _builds_from_mongo_cursor(self, mongo_cursor):
        builds = []
        for build in mongo_cursor:
            build_dict = {}
            for k, v in build.items():
                build_dict[k.__str__()] = v.__str__()
            builds.append(build_dict)
        return builds
