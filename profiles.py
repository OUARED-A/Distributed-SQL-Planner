from collections import namedtuple
from operator import attrgetter
from eqclass import eqclass
from alias import Alias
from utils import flat

aliases = Alias(set)

def antialias(columns):
    return set(flat(map(aliases, columns)))

class Profile(namedtuple('Profile', 'v e iv ie sim')):

    @staticmethod
    def build(node, inputs):
        return _profiles[node.get('relOp')](node, inputs)


def _get_operands_from(field):
    if isinstance(field, list): return [flat(map(_get_operands_from, field))]
    if not isinstance(field, dict): return [[]]
    if 'input' in field: return [[field['input']]]
    if 'agg' in field: return [field['operands']]
    ops = [x for op in field['operands'] for x in _get_operands_from(op) if x]
    return [flat(ops)] if field['op'] not in ('AND', 'OR') else ops


def _get_column_groups_from(node, field=None, cols=None):
    operands = _get_operands_from(field or node.get('condition'))
    columns = cols or node.get('cols')
    return [set(map(columns.__getitem__, op)) for op in operands if op]


def tablescan(node, inputs):
    assert not inputs
    return Profile(set(node.get('cols')),
        set(), set(), set(), eqclass())


def projection(node, inputs):
    assert len(inputs) == 1
    pl = inputs[0].profile
    exprs = _get_column_groups_from(node, node.get('exprs'),
                                    inputs[0].node.get('cols'))
    assert len(exprs) == 1
    fields = exprs[0]
    return pl._replace(v=pl.v & fields, e=pl.e & fields)


def selection(node, inputs):
    assert len(inputs) == 1
    pl = inputs[0].profile

    for columns in map(antialias, _get_column_groups_from(node)):
        if not columns <= pl.v | pl.e:
            raise ValueError('some columns %s not in children' % columns)
        if len(columns) > 1:          # update equivalence class
            pl = pl._replace(sim=eqclass(columns).merge(pl.sim))
        elif columns <= pl.v:         # plaintext
            pl = pl._replace(iv=pl.iv | columns)
        else:                         # encrypted
            assert columns <= pl.e
            pl = pl._replace(ie=pl.ie | columns)
    return pl


def join(node, inputs):
    assert len(inputs) == 2
    pl, pr = (input.profile for input in inputs)
    sim = eqclass(_get_column_groups_from(node)).merge(pl.sim).merge(pr.sim)
    return Profile(v=pl.v | pr.v, e=pl.e | pr.e, iv=pl.iv | pr.iv,
                   ie=pl.ie | pr.ie, sim=sim)


def aggregate(node, inputs):
    assert len(inputs) == 1
    pl = inputs[0].profile

    exprs = filter(lambda col: '$' in col, node.get('cols'))
    aggs = node.get('aggs')
    assert len(exprs) == len(aggs)
    cols = inputs[0].node.get('cols')
    for agg, expr in zip(aggs, exprs):
        alias = set.union(*_get_column_groups_from(node, agg, cols))
        if expr not in aliases:
            aliases[expr] = alias
        else:
            assert aliases[expr] == alias
    return pl


def jdbctoenumerate(node, inputs):
    assert len(inputs) == 1
    return inputs[0].profile


_profiles = {
    'JdbcTableScan': tablescan,
    'JdbcProjectRel': projection,
    'JdbcFilterRel': selection,
    'JdbcJoinRel': join,
    'JdbcAggregateRel': aggregate,
    'JdbcToEnumerableConverter': jdbctoenumerate
}
