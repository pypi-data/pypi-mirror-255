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
"""
Script to create  RPM Spec files

"""
import logging
import os
import argparse
import re
import sys
from string import Template
from lbinstall.Installer import Installer
from pprint import pprint

log = logging.getLogger()
log.setLevel(logging.INFO)


# Tools to retrieve the list fo externals
#############################################################
def getExternalsList(filename):
    '''
    Gets the list of all externals needed (as from LCG 86)
    '''
    log.warning("Loading list of externals from file")
    # Cache the externals dictionary for the version...
    # Loading the metadata
    import json
    with open(filename) as f:
        data = json.load(f)

        # Looking for LCG version
        # We need a file like so:
        # {
        #  "heptools": {
        #    "version": 84
        #    "packages":[
        #      "AIDA",
        #      "Boost",
        #      "CLHEP",
        #      "COOL"
        #    ]
        #    "package_versions":
        #     [
        #      ["genratorX, "1.0"]
        #
        #    ]
        #  }
        # }

    heptools = data["heptools"]
    lcgver = heptools["version"]
    externals_list = heptools.get("packages", list())
    externals_version_list = heptools.get("package_versions", list())
    return (lcgver, externals_list, externals_version_list)



lhcb_installer = None

class VersionFinder(object):
    """ Utility class to cache the DB """
    def __init__(self, lcgVersion, cmtconfig, siteroot="/tmp/siteroot"):
        self.siteroot = siteroot
        self.lcgVersion = lcgVersion
        self.cmtconfig = cmtconfig
        self.packages = None
        self.rpms = None

    def setup(self):
        global lhcb_installer
        if lhcb_installer is None:
            lhcb_installer = Installer(self.siteroot)
        if self.packages is None or self.rpms is None:
            self.rpms = [ p for p in lhcb_installer.remoteListPackages('LCG_%s_' % self.lcgVersion) ]
            self.packages = {p.name for p in self.rpms}
            
    def find(self, package):
        self.setup()
        extName = "^%s.*$" % buildLCGName(self.lcgVersion, re.escape(package), ".*", re.escape(self.cmtconfig.replace("-", "_")))
        plist = []
        for p in self.packages:
            if re.match(extName, p):
                plist.append(p)
        return plist

    def find_rpm(self, package):
        self.setup()
        extName = "^%s.*$" % buildLCGName(self.lcgVersion, re.escape(package), ".*", re.escape(self.cmtconfig.replace("-", "_")))
        plist = []
        for p in self.rpms:
            if re.match(extName, p.rpmName()):
                plist.append(p)
        return plist


    def check(self, package, version):
        self.setup()
        extName = buildLCGName(self.lcgVersion, package, version, self.cmtconfig.replace("-", "_"))
        return extName in self.packages

def buildLCGName(lcgVersion, package, version, cmtconfig):
    return "LCG_%s_%s_%s_%s" % (lcgVersion, package, version, cmtconfig.replace("-", "_"))

def getRequiresList(cmtconfig, filename, siteroot="/tmp/siteroot"):
    # Setting the CMTCONFIG to the requested one
    os.environ['CMTCONFIG'] = cmtconfig

    # Retrieving the list of externals from the mentioned project
    (lcgVer, externals_list, external_versions_list) = getExternalsList(filename)
    vf = VersionFinder(lcgVer, cmtconfig)

    found = []
    missing = []

    # Looking up the versions of packages specified without version first
    for package in externals_list:
        res = vf.find(package)
        if not res:
            missing.append(package)
            log.warning("Could not find package %s in LCG %s %s" % (package, lcgVer, cmtconfig))
        else:
            found += res

    # Checking if the packages specified with version are correct
    for (package, version) in external_versions_list:
        if not vf.check(package, version):
            missing.append(package)
            log.warning("Could not find package %s %s in LCG %s %s" % (package, version, lcgVer, cmtconfig))
        else:
            found.append(buildLCGName(lcgVer, package, version, cmtconfig))

    return(lcgVer, found)

def getRequiresNoLinkRPM(cmtconfig, filename, siteroot="/tmp/siteroot"):
    # Setting the CMTCONFIG to the requested one
    os.environ['CMTCONFIG'] = cmtconfig

    # Retrieving the list of externals from the mentioned project
    (lcgVer, externals_list, external_versions_list) = getExternalsList(filename)
    vf = VersionFinder(lcgVer, cmtconfig)

    found = []
    missing = []

    # Looking up the versions of packages specified without version first
    for package in externals_list:
        res = vf.find_rpm(package)
        if not res:
            missing.append(package)
            log.warning("Could not find package %s in LCG %s %s" % (package, lcgVer, cmtconfig))
        else:
            deps = [  r.name for r in res[0].requires if r.name.startswith(package)] 
            if not deps or len(deps) > 1:
                print(f"Error finding dependencies for {package}: {deps}")
            found.append(deps[0])

    # Checking if the packages specified with version are correct
    for (package, version) in external_versions_list:
        if not vf.check(package, version):
            missing.append(package)
            log.warning("Could not find package %s %s in LCG %s %s" % (package, version, lcgVer, cmtconfig))
        else:
            res = vf.find_rpm(package)
            deps = [  r.name for r in res[0].requires if r.name.startswith(package)] 
            if not deps or len(deps) > 1:
                print(f"Error finding dependencies for {package}: {deps}")
            found.append(deps[0])


    return(lcgVer, found)



###############################################################################
# Class to build the SPEC itself
###############################################################################

class LHCbLCGMetaSpec(object):
    """ Class presenting the whole spec """

    def __init__(self, name, version, platform, requiresList, rpmroot, release="1"):
        """ Initialize with the list of RPMs """
        self.name = name
        self.rpmname = name
        self.version = version
        self.platform = platform
        self.requiresList = requiresList
        self.rpmroot = rpmroot
        self.release = release

        # Building the build dir paths
        myroot = rpmroot
        self.topdir = "%s/rpmbuild" % myroot
        self.tmpdir = "%s/tmpbuild" % myroot
        self.rpmtmp = "%s/tmp" % myroot
        self.srcdir = os.path.join(self.topdir, "SOURCES")
        self.rpmsdir = os.path.join(self.topdir, "RPMS")
        self.srpmsdir = os.path.join(self.topdir, "SRPMS")
        self.builddir = os.path.join(self.topdir, "BUILD")

        # And creating them if needed
        for d in [self.srcdir, self.rpmsdir, self.srpmsdir, self.builddir]:
            if not os.path.exists(d):
                os.makedirs(d)

        self.buildroot = os.path.join(self.tmpdir, "%s-%s-%s-buildroot" % \
                                      (self.name, self.version, self.platform))
        if not os.path.exists(self.buildroot):
            os.makedirs(self.buildroot)

    def getHeader(self):
        """ Build the SPEC Header """
        rpm_header = Template("""
%define version $version
%define platform $platform
%define platformFixed $platformFixed

%define _topdir $topdir
%define tmpdir $tmpdir
%define _tmppath $rpmtmp
%define debug_package %{nil}
%global __os_install_post /usr/lib/rpm/check-buildroot

Name: $rpmname
Version: 1.0.0
Release: $release
Vendor: LHCb
Summary: LCG  %{version} %{platform} for LHCb
License: GPL
Group: LCG
BuildRoot: %{tmpdir}/LCGLHCb-%{version}-%{platform}-buildroot
BuildArch: noarch
AutoReqProv: no
Prefix: /opt/LHCbSoft
Provides: /bin/sh
Provides: LCG_%{version}LHCb_%{platformFixed}

""").substitute(rpmname=self.rpmname,
                version=self.version,
                platform=self.platform,
                platformFixed=self.platform.replace("-", "_"),
                topdir=self.topdir,
                tmpdir=self.tmpdir,
                rpmtmp=self.rpmtmp,
                release=self.release)
        return rpm_header

    # RPM requirements for the whole package
    #############################################################

    def getRequires(self):
        rpm_requires = ""
        for r in self.requiresList:
            rpm_requires += "Requires: %s\n" % r

        return rpm_requires

    # RPM Description section
    #############################################################

    def getDescriptions(self):
        rpm_desc = """
%description
LCG externals %{version} %{platform} for LHCb

"""
        return rpm_desc

    # RPM Common section with build
    #############################################################

    def getCommon(self):
        rpm_common = """
%prep

%build

%install

%files

%post

%postun

%clean
"""
        return rpm_common

    # RPM Trailer
    #############################################################

    def getTrailer(self):
        rpm_trailer = """
%define date    %(echo `LC_ALL=\"C\" date +\"%a %b %d %Y\"`)

%changelog

* %{date} User <ben.couturier..rcern.ch>
- first Version
"""
        return rpm_trailer

    # Get the whole spec...
    #############################################################

    def getSpec(self):
        """ Concatenate all the fragments """

        rpm_global = self.getHeader() \
                     + self.getRequires() \
                     + self.getDescriptions() \
                     + self.getCommon() \
                     + self.getTrailer()

        return rpm_global


def createSpec(platform, filename, output=None, release = "1", rpmname=None, rpmroot="/tmp", return_required=False):

    # Getting the list of RPMs to add
    if return_required:
        (lcgVer, requiresList) = getRequiresNoLinkRPM(platform, filename)
    else:
        (lcgVer, requiresList) = getRequiresList(platform, filename)

    print("LGC Version: %s" % lcgVer)
    print("Requires list:")
    pprint(requiresList)

    if rpmname is None:
        rpmname = "LCG_%sLHCb_%s" % (lcgVer, platform.replace("-", "_"))
    spec = LHCbLCGMetaSpec(rpmname, lcgVer, platform, requiresList, rpmroot, release)

    if output:
        with open(output, "w") as outputfile:
            outputfile.write(spec.getSpec())
        log.info("written output to %s" % output)
        return output
    else:
        print(spec.getSpec())
    log.info("Spec file generated")


###############################################################################
# Main method
###############################################################################
def main():
    # Parsing options
    desc = "Prepare the SPEC file the LHCb Meta RPM given the list of needed externals"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('platform', help="Platform e.g. x86_64-centos7-gcc7-opt to compile against")
    parser.add_argument('external_list_json', help="JSON file describing the list of externals to install")
    parser.add_argument('-d', '--debug', action='store_const',
                        const=logging.DEBUG, dest='log_level')
    parser.set_defaults(log_level=logging.WARNING)
    parser.add_argument('-b', '--buildroot',
                      dest="buildroot",
                      default="/tmp",
                      action="store",
                      help="Force build root")
    parser.add_argument('-o', '--output',
                      dest="output",
                      default=None,
                      action="store",
                      help="File name for the generated specfile [default output to stdout]")
    parser.add_argument("-s", "--siteroot",
                      help="temporary directory where the RPMs will be installed before repackaging"
                           "[default: %default]",
                      default="/tmp/siteroot")
    parser.add_argument("-r", "--release",
                      help="Release number"
                           "[default: %default]",
                      default="1")
    parser.add_argument("-n", "--name",
                      help="Name of the package being produced"
                           "[default: %default]",
                      default=None)
    parser.add_argument("--require-base-package",
                      help="require the real package with checksum instead of the RPM with symlink",
                      default=False,
                      action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level, stream=sys.stderr)
    createSpec(args.platform, args.external_list_json, args.output, release=args.release, rpmname=args.name, rpmroot=args.buildroot, return_required=args.require_base_package)

if __name__ == '__main__':
    main()
