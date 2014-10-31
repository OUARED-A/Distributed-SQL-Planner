from collections import namedtuple, Counter
from itertools import product, chain
from operator import methodcaller
from profiles import Profile
from server import Servers
from utils import memo, listify
import logging


class Plan(namedtuple('Plan', 'root profile executers costs profiles rows node')):

    def totalcost(self):
        return sum(self.costs.values())

    def serverid(self):
        return self.executers[self.root]

    def __str__(self):
        return '[Plan cost={:g} {{{}}} nodes={{{}}}]'.format(
            self.totalcost(),
            ', '.join('%s:%g' % data for data in self.costs.most_common()),
            ', '.join('%s:%s' % data for data in
                sorted(self.executers.iteritems(), key=lambda x: int(x[0]))))


class Planner:

    def __init__(self, servers):
        self._servers = Servers(servers)

    @memo
    @listify
    def _plans_default(self, node, servers=None):
        for inputplans in product(*map(self.get_plans, node.inputs)):
            profile = Profile.build(node, inputplans)
            for server in servers or self._servers:
                authorized = self._servers.authorize(profile, server.id)
                if authorized:
                    yield self.makeplan(node, inputplans, server, authorized)

    @memo
    @listify
    def _plans_tablescan(self, node):
        tbl = node.get('table')[1]
        profile = Profile.build(node, None)
        for server in [s for s in self._servers if tbl in s.tables]:
            authorized = self._servers.authorize(profile, server.id)
            if authorized:
                yield self.makeplan(node, [], server, authorized)

    @memo
    def _plans_enumerable(self, node):
        return self._plans_default(node, [self._servers['CL']])

    @memo
    def _planfn(self, relOp):
        planfn = { 'JdbcToEnumerableConverter': self._plans_enumerable,
                  'JdbcTableScan': self._plans_tablescan }
        try:
            return planfn[relOp]
        except:
            return self._plans_default

    @memo
    def get_plans(self, node):
        plans = self._planfn(node.get('relOp'))(node)
        logging.debug( '#%d plans for node %s' % (len(plans), node.get('id')))
        return plans

    def get_best_plan(self, node):
        plans = self.get_plans(node)
        return min(plans, key=methodcaller('totalcost')) if plans else None

    def makecost(self, node, inputplans, server):
        nodecost = node.get('cost')
        costs = Counter({server.id:
            server.cpu * nodecost['cpu'] + server.io * nodecost['io']})
        for plan in inputplans:
            inserver = self._servers[plan.serverid()]
            if inserver is not server:
                costs['%s->*' % inserver.id] += plan.rows * inserver.netout
                costs['*->%s' % server.id] += plan.rows * server.netin
        return costs

    def makeplan(self, node, inputplans, server, profile):
        root = node.get('id')
        rows = node.get('rowCount')
        executers = dict(chain.from_iterable(
            plan.executers.iteritems() for plan in inputplans))
        executers[root] = server.id
        profiles = dict(chain.from_iterable(
            plan.profiles.iteritems() for plan in inputplans))
        profiles[root] = profile
        costs = sum((plan.costs for plan in inputplans),
            self.makecost(node, inputplans, server))
        return Plan(root, profile, executers, costs, profiles, rows, node)
