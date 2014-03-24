#!/usr/bin/env python3
# encoding: utf-8
'''
Simple CLI script to use gerritssh to talk to a site

This is a simple script intended to be used in testing gerritssh against
live Gerrit instances (instead of the mock ones used in the unit tests).

'''

import sys
import logging

import argparse
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter


import gerritssh as gssh

__all__ = []
__version__ = gssh.__version__

######################################################################
#
# Set up the root logger so that log statements in the library will
# actually display. Without a StreamHandler(), the NullHandler in the
# library simply swallows all the logs.
#
######################################################################

log = logging.getLogger()
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
log.addHandler(_handler)

################################################################
#
# The following functions actually demonstrate using the library
#
################################################################


def connect_to_site(site):
    ''' Connect to the specified site '''
    return gssh.Site(site).connect()


def version_cmd(site, args):
    ''' Print the version of Gerrit running on the connected Site '''
    vstr = str(site.version)
    print('{0} is running version {1} of Gerrit'.format(site.site,
                                                        vstr))
    return 0


def query_cmd(site, args):
    '''
    Execute the query command and print out the results
    grouped by project and ordered by change number.
    '''
    b = 'branch:{0}'.format(args.branch) if args.branch else ''
    p = 'project:{0}'.format(args.project) if args.project else ''
    s = 'status:{0}'.format(args.qstatus) if args.qstatus else ''
    q = ' '.join(args.querystring) if args.querystring else ''
    q = gssh.Query(' '.join([b, p, s, q]), max_results=args.maxresults or 0)
    log.debug('Executing query command {0} on {1}'.format(q._Query__query,
                                                          site.site))
    q.execute_on(site)

    last_project = ''
    for r in sorted(q, key=lambda rvw: ' '.join([rvw.project, rvw.ref])):
        if r.project != last_project:
            print('\n{0}:'.format(r.project))
            last_project = r.project
        print('\t({0})\t{1}'.format(r.ref, r.summary))
    return 0


def lp_cmd(site, args):
    ''' List the projects on the connected Site '''
    lp = gssh.ProjectList(args.listall)
    lp.execute_on(site)
    for p in lp:
        print(p)
    return 0


def execute(args):
    try:
        site = connect_to_site(args.site)
    except gssh.SSHConnectionError as e:
        print(e)
        sys.exit(1)

    log.debug('Connected Successfully')

    cmds = {'query': query_cmd,
            'projects': lp_cmd,
            'version': version_cmd}
    cmds[args.operation](site, args)
    return 0

################################################################
#
# The rest of the file is all about parsing the command line
#
################################################################


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


def parse_command_line():
    program_version = "v%s" % __version__

    program_license = '''
  Copyright 2014 Keith Derrick. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.
'''

    program_version_message = '%%(prog)s %s\n\n%s' % (program_version,
                                                     program_license)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]

    # Setup argument parser
    parser = ArgumentParser(description=program_shortdesc,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", dest="verbose", action="count",
                        help="set verbosity level [default: %(default)s]")
    parser.add_argument('-V', '--version', action='version',
                        version=program_version_message)

    subparsers = parser.add_subparsers(dest='operation')
    subparsers.required = True
    lp_parser = subparsers.add_parser('projects',
                                      help='List the projects')
    lp_parser.add_argument('site',
                           help=('The Gerrit instance to connect to, '
                                 'e.g review.openstack,org'))
    lp_parser.add_argument('-a', '--all', dest='listall',
                           action='store_true', default=False,
                           help='List all project types')

    query_parser = subparsers.add_parser('query',
                                         help='Search for reviews')
    query_parser.add_argument('site',
                              help=('The Gerrit instance to connect to, '
                                    'e.g review.openstack,org'))
    query_parser.add_argument('-s', '--status', dest='qstatus',
                              choices=['open', 'merged', 'abandoned'],
                              help='Find all reviews with he given status')
    query_parser.add_argument('-b', '--branch', dest='branch',
                              help='Restrict search to a given branch')
    query_parser.add_argument('-l', '--limit', dest='maxresults',
                              type=int,
                              help='Limit the number of results')
    query_parser.add_argument('-p', '--project', dest='project',
                              help='Project for which reviews are required')
#     query_parser.add_argument('--', dest='query string',
#                               help='Standard query options and flags')
    query_parser.add_argument('querystring', metavar='QUERY',
                              nargs=argparse.REMAINDER)

    v_parser = subparsers.add_parser('version', help='Show the Gerrit version')
    v_parser.add_argument('site',
                          help=('The Gerrit instance to connect to, '
                                'e.g review.openstack,org'))

    # Process arguments
    args = parser.parse_args()
    # Set the logging level
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    verbose = args.verbose or 0
    log.setLevel(levels[max(min(verbose, 2), 0)])
    log.debug('parser results: {0}'.format(args))
    return args


if __name__ == "__main__":
    args = parse_command_line()
    execute(args)
