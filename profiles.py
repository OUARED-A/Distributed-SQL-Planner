from collections import namedtuple
from operator import attrgetter
from eqclass import eqclass
from copy import deepcopy


class Profile(namedtuple('Profile', 'v e iv ie sim')):

    @staticmethod
    def build(node, inputs):
        return _profiles[node.get('relOp')](node, inputs)


def tablescan(node, inputs):
    assert not inputs
    return Profile(set(node.get('cols')),
        set(), set(), set(), eqclass())


def projection(node, inputs):
    assert len(inputs) == 1
    pl = inputs[0].profile
    fields = set(node.get('fields'))
    return pl._replace(v=pl.v & fields, e=pl.e & fields)


def _get_columns_from_condition(node):
    return set(node.get('cols')[operand['input']]
               for operand in node.get('condition')['operands']
               if isinstance(operand, dict))


def selection(node, inputs):
    assert len(inputs) == 1
    pl = inputs[0].profile
    columns = _get_columns_from_condition(node)

    if len(columns) > 1:       # update equivalence class
        pl = pl._replace(sim=deepcopy(pl.sim).add(*columns))
    if columns <= pl.v:        # both visible
        return pl._replace(iv=pl.iv | columns)
    elif columns <= (pl.v | pl.e):
        return pl._replace(v=pl.v - columns,
            e=pl.e | columns, ie=pl.ie | columns)
    raise ValueError('selected columns not in child')


def join(node, inputs):
    assert len(inputs) == 2
    pl, pr = (input.profile for input in inputs)
    columns = _get_columns_from_condition(node)
    profile = Profile(v=pl.v | pr.v, e=pl.e | pr.e,
                      iv=pl.iv | pr.iv, ie=pl.ie | pr.ie | columns,
                      sim=deepcopy(pl.sim).merge(pr.sim).add(*columns))
    return (profile if columns <= profile.v else
            profile._replace(v=profile.v - columns, e=profile.e | columns))


def aggregate(node, inputs):
    assert len(inputs) == 1
    return inputs[0].profile


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
