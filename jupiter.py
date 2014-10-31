#!/usr/bin/env python

from operator import methodcaller
from relplan import Planner
import subprocess
import argparse
import logging
import reltree
import os.path
import json
import sys

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
jupiter = ['java', '-jar', 'lib/jupiter.jar']

def main(args):
    try:
        if not os.path.isfile(args.SERVERS):
            print 'Server configuration file not found: %s' % args.SERVERS
            sys.exit(1)
        output = subprocess.check_output(jupiter + ['--json'] + sys.argv[2:])
    except subprocess.CalledProcessError as e:
        print e.output
        sys.exit(1)

    root = reltree.parse(output)
    print '=== Parsed Tree ==='
    print root

    print '=== Generation ==='
    planner = Planner(args.SERVERS)
    plans = planner.get_plans(root)

    print '\n=== Plans ==='
    for plan in sorted(plans, key=methodcaller('totalcost'), reverse=True):
        print plan

    print '\n=== Best Plan ==='
    bestplan = planner.get_best_plan(root)
    print bestplan
    print root.print_with_plan(bestplan)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Use Optiq to get a relational plan from SQL statement.')
    parser.add_argument('-n', '--no-opt', action='store_true', dest='no-opt',
        help='Convert SQL to a relational plan but do not optimize')
    parser.add_argument('-j', '--json', dest='json', action='store_true',
        help='Output the result as JSON')
    parser.add_argument('SERVERS', help='Servers configuration file')
    parser.add_argument('DB', help='SQLite database to use as schema source')
    parser.add_argument('SQL', help='SQL query (quote it as a single string)')
    main(parser.parse_args())
