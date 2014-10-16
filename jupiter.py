#!/usr/bin/env python

from operator import methodcaller
from relplan import Planner
import subprocess
import reltree
import json
import sys

jupiter = ['java', '-jar', 'lib/jupiter.jar']
servers = 'config/servers'

def main():
    try:
        output = subprocess.check_output(jupiter + ['--json'] + sys.argv[1:])
    except subprocess.CalledProcessError as e:
        print e.output
        sys.exit(1)

    root = reltree.parse(output)
    print '=== Parsed Tree ==='
    print root

    print '=== Generation ==='
    planner = Planner(servers)
    plans = planner.get_plans(root)

    print '\n=== Plans ==='
    for plan in sorted(plans, key=methodcaller('totalcost'), reverse=True):
        print plan

    print '\n=== Best Plan ==='
    bestplan = planner.get_best_plan(root)
    print bestplan
    print root.print_with_plan(bestplan)

if __name__ == '__main__':
    main()
