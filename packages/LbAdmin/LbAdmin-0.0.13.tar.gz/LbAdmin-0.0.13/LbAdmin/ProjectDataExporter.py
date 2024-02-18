###############################################################################
# (c) Copyright 2019 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
__author__ = 'Ben Couturier <ben.couturier@cern.ch>'


from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBase
from collections import defaultdict
import json
import logging
import argparse

DEFAULT_FILENAME="SoftCondDBCache.json"

class JSONSoftConfDBCache(object):
    """  Class that creates the JSON cache with the LHCb project information """
    @classmethod
    def create(cls, softconfdb, filename=DEFAULT_FILENAME):
        """ Static factory for the JSON file """
        db = defaultdict(dict)
        projects = softconfdb.listProjects()
        for project in projects:
            logging.info("Processing %s" % project)
            versions = softconfdb.listVersions(project)
            vp = dict()
            for version in versions:
                p, v = version
                platforms = softconfdb.listPlatforms(p, v)
                vp[v] = platforms
            db[project] = vp
        with open(filename, "wt") as f:
            json.dump(db, f, indent=4)

    def __init__(self, filename=DEFAULT_FILENAME):
        """ Constructor that loads the DB """
        with open(filename, "rt") as f:
            self.db = json.load(f)

    def listPlatforms(self, project, version):
        """ List the platforms for the project version or trigger
        and exception if iot does not exist"""
        vp = self.db[project.upper()]
        return vp[version]


def export():
    """ Script method that takes the outputfilename as argument """
    logging.basicConfig(level=logging.INFO)
    sdb = LbSoftConfDbBase().getROInterface(noCertVerif=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("outputfile")
    args = parser.parse_args()
    JSONSoftConfDBCache.create(softconfdb=sdb, filename=args.outputfile)


if __name__ == "__main__":
    export()


