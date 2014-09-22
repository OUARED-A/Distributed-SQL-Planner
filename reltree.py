from collections import defaultdict
from copy import deepcopy
import json


def parse(output):
    tree = json.loads(output)
    nodes = {node['id']: RelNode(node) for node in tree['rels']}
    for node in nodes.values():
        node.inputs = map(nodes.get, node.data.get('inputs', []))
    return nodes[tree['root']]


class RelNode:

    def __init__(self, data):
        self.data = deepcopy(data)
        self.inputs = []

    def get(self, key):
        return self.data[key]

    def pprint(self, indent=0, exes=defaultdict(str), profs=defaultdict(str)):
        id = self.data['id']
        return ('%s%s%s: %s %s\n' % (
                ' ' * indent, id, exes[id], self.data, profs[id]) +
            ''.join(nd.pprint(indent + 2, exes, profs) for nd in self.inputs))

    def print_with_plan(self, plan):
        return self.pprint(exes=plan.executers, profs=plan.profiles)

    def fix(self, db):
        fixes.fixtree(self, db)

    def __str__(self):
        return self.pprint()
