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
Script to generate all RPM files in one go

"""
import json
import logging
import argparse
import os
import sys
from  LbAdmin.CreateLHCbLCGMetaSpec import createSpec

log = logging.getLogger()
log.setLevel(logging.INFO)

# Utils
#############################################################
def get_LCG_version(externals_filename):
    with open(externals_filename) as f:
        data = json.load(f)
    heptools = data["heptools"]
    lcgver = heptools["version"]
    return lcgver

###############################################################################
# Main method
###############################################################################
def main():
    
    # Parsing options
    parser = argparse.ArgumentParser(description="Prepare all the SPEC files for the externals/platforms listed")
    parser.add_argument('name_template', help="name template for the RPM of the form: LCG_{lcg_version}LHCb_{platform}")
    parser.add_argument('platform_list_file', help="File containing the list of platforms")
    parser.add_argument('external_list_json', help="JSON file describing the list of externals to install")
    parser.add_argument('-d', '--debug', action='store_const',
                       const=logging.DEBUG, dest='log_level')
    parser.set_defaults(log_level=logging.WARNING)
    parser.add_argument('-b', '--buildroot',
                      dest="buildroot",
                      default="/tmp",
                      action="store",
                      help="Force build root")
    parser.add_argument("-r", "--release",
                      help="Release number"
                           "[default: 1]",
                      default="1")
    parser.add_argument("--require-base-package",
                      help="require the real package with checksum instead of the RPM with symlink",
                      default=False,
                      action='store_true')
    args = parser.parse_args()

    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, stream=sys.stderr)

    # Reading some date from the files
    lcg_version = get_LCG_version(args.external_list_json)
    platforms = []
    with open(args.platform_list_file) as f:
        platforms += [ l.strip() for l in f.readlines() if l]

    specs = []
    for p in platforms:
        rpmname = args.name_template.format(lcg_version=lcg_version, platform=p)
        output = rpmname + ".spec"
        f = createSpec(p, args.external_list_json, output, release=args.release,
                        rpmname=rpmname, rpmroot=args.buildroot, return_required=True)
        print("Created {}".format(f))
        specs.append(f)

    print("To generate the RPMs run:")
    for s in specs:
        print("rpmbuild -bb {}".format(s))


if __name__ == '__main__':
    main()
