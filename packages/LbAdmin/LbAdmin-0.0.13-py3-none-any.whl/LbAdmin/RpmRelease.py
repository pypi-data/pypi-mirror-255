#!/usr/bin/env python
# $Id: $
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


import os
import sys
import re
import json
from subprocess import Popen, PIPE
import shutil
import datetime
from LbCommon.Script import Script
from xml.dom import minidom
from urllib.request import urlopen
from datetime import date


def ReSyncRepoJson(repopath,
                   baseUrl="http://lhcb-rpm.web.cern.ch/lhcb-rpm"):
    repopath = os.path.abspath(repopath)
    if repopath.endswith('.json'):
        jsonFilePath = repopath
    else:
        jsonFilePath = "%s/repoinfo.json" % repopath
    data_has_changed = False
    json_data = {}
    if os.path.exists(jsonFilePath):
        with open(jsonFilePath, "r") as f:
            json_data = json.load(f)
    else:
        raise IOError("No json file found!")
    for repo in json_data:
        repodir = json_data[repo]['url']
        # stripping end / as some servers (S3) cannot cope with multiple / 
        xml_repo_info_url = "%s/repodata/repomd.xml" % repodir.rstrip("/")
        time = None
        response = urlopen(xml_repo_info_url)
        xml_repo_info = response.read()
        xmldoc = minidom.parseString(xml_repo_info)
        itemlist = xmldoc.getElementsByTagName('data')
        for type_tag in itemlist:
            if type_tag.attributes['type'].value in ('primary_db', 'primary'):
                date_tag = type_tag.getElementsByTagName('timestamp')
                time = int(float(date_tag[0].firstChild.nodeValue))
                time = datetime.datetime.fromtimestamp(time).strftime(
                    '%Y-%m-%d %H:%M:%S')
        if time != json_data[repo]['last_update']:
            json_data[repo]['last_update'] = time
            data_has_changed = True
    if data_has_changed:
        with open(jsonFilePath, "w") as f:
            json.dump(json_data, f, indent=4, separators=(',', ': '),
                      sort_keys=True)


class ReSyncRepoMetainfo(Script):

    def __init__(self):
        Script.__init__(self, usage="\n\t%prog [options] path-to-config",
                        description="Script to regernati the repos meta info "
                                    "configuration file")

    def main(self):
        ''' Main method for the script '''
        if len(self.args) != 1:
            self.parser.error('Please specify the directory with the '
                              'repoinfo.json or the configuration '
                              'file you want to update')
        else:
            try:
                ReSyncRepoJson(self.args[0])
            except Exception as e:
                self.parser.error(str(e))

# @class ReleaseSlot
# Main script class for to release RPMs to the repository.
class ReleaseSlot(Script):

    def __init__(self):
        Script.__init__(self, usage="\n\t%prog [options] <release build id|rpms dir>",
                        description="Script to copy RPMs to the LHCb "
                                    "RPM repository and reindex the DB")

    def defineOpts(self):
        ''' User options '''
        self.parser.add_option("-i", "--interactive", action="store_true",
                               default=False,
                               help="Prompt before copying the files")
        self.parser.add_option("-r", "--rpm-dir", action="store",
                               default="/eos/project/l/lhcbwebsites/www/lhcb-rpm/lhcb{}".format(date.today().year),
                               help="Location of default repo [default: %default]")
        self.parser.add_option("--rpm-regex", action="store", default=None,
                               help="Regexp for the RPM names to copy")
        self.parser.add_option("-c", "--copy", action="store_true",
                               default=False,
                               help="Really copy the files, "
                                    "in dry-run mode otherwise")

    def releaseRpms(self, builddir, repodir, copymode, rpmre):
        ''' Release the RPMs in builddir to the RPM repo '''

        if builddir.isdigit():
            builddir = "/eos/project/l/lhcbwebsites/www/lhcb-nightlies-artifacts/release/lhcb-release/{}/rpms".format(builddir)

        builddir = os.path.abspath(builddir)
        repodir = os.path.abspath(repodir)

        self.log.warning("Build dir: %s" % builddir)
        self.log.warning("Repo  dir: %s" % repodir)

        if not os.path.exists(builddir):
            raise Exception("The build directory %s does not exist" % builddir)

        if not os.path.exists(repodir):
            raise Exception("The RPM repository %s does not exist" % repodir)

        # Listing the RPMs in the build dir
        rpms = [f for f in os.listdir(builddir) if f.endswith(".rpm")]

        # Iterating on the rpms
        newrpms = []
        import re
        for rpm in rpms:
            if rpmre is not None:
                if not re.match(rpmre, rpm):
                    continue

            rpminbuild = os.path.join(builddir, rpm)
            rpminrepo = os.path.join(repodir, rpm)
            if os.path.exists(rpminrepo):
                self.log.warning("RPM EXISTS: %s already in repository" % rpm)
            else:
                self.log.warning(
                    "RPM NEW   : %s will be copied to repository" % rpm)
                if copymode:
                    shutil.copy(rpminbuild, repodir)
                    newrpms.append(rpm)

        # Returning
        return newrpms

    def updateRepoDB(self, repodir):
        ''' Recreate/Update the YUM repository DB  '''

        if not os.path.exists(repodir):
            raise Exception("The RPM repository %s does not exist" % repodir)

        self.log.warning("Updating RPM repository %s" % repodir)
        os.system("createrepo --workers=20 --update %s" % repodir)
        repopath = repodir
        if repopath[-1] == '/':
            repopath = repopath[0:-1]
        repopath = os.path.dirname(repopath)
        ReSyncRepoJson(repopath)

    def main(self):
        ''' Main method for the script '''
        if len(self.args) != 1:
            self.parser.error('Please specify the release build id or the directory with the RPMs')

        if not self.options.copy:
            self.log.warning(
                "In dry-run mode. use --copy to perform the actual copy")
        else:
            self.log.warning("Copying RPMs to the YUM repository")

        copiedrpms = self.releaseRpms(self.args[0],
                                      self.options.rpm_dir,
                                      self.options.copy,
                                      self.options.rpm_regex)
        if len(copiedrpms) > 0 and self.options.copy:
            self.updateRepoDB(self.options.rpm_dir)


def release():
    return ReleaseSlot().run()


def resync():
    return ReSyncRepoMetainfo().run()
