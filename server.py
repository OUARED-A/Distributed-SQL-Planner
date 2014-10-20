from collections import namedtuple
from utils import memo
import json

Server = namedtuple('Server', 'id tables cpu io netin netout')
Table = namedtuple('Table', 'name columns authorizations')
Authorization = namedtuple('Authorization', 'server v e')


class Servers:

    _types = [(Server, 'id', 'tables', True),
              (Table, 'name', 'authorizations', True),
              (Authorization, 'server', 'server', False)]

    @staticmethod
    def _obj_hook(dct):
        for cls, id, key, todict in Servers._types:
            if key in dct:
                if todict:
                    dct[key] = dict(dct[key])
                return (dct[id], cls(**dct))

    def __init__(self, filename):
        with open(filename, 'rb') as f:
            self._servers = dict(json.load(f, object_hook=Servers._obj_hook))

    def __iter__(self):
        return self._servers.itervalues()

    def __getitem__(self, key):
        return self._servers[key]

    def __str__(self):
        return str(self._servers)

    @memo
    def _table_with(self, column):
        return next(table for srv in self._servers.values()
            for table in srv.tables.values() if column in table.columns)

    @memo
    def _get_authz(self, column, srv_id):
        tbl = self._table_with(column)
        authzs = tbl.authorizations
        try:
            return authzs.get(srv_id, None) or authzs['*']
        except KeyError:
            raise KeyError('No authz server:%s table:%s' % (srv_id, tbl.name))

    def _check_v(self, cols, srv_id):
        return all(col in self._get_authz(col, srv_id).v for col in cols)

    def _check_e(self, cols, srv_id):
        return all(col in self._get_authz(col, srv_id).e for col in cols)

    def _check_v_or_e(self, cols, srv_id):
        return all(col in self._get_authz(col, srv_id).v or
                   col in self._get_authz(col, srv_id).e for col in cols)

    def _check_sim(self, profile, srv_id):
        return all(self._check_v(cols, srv_id) or self._check_e(cols, srv_id)
                   for cols in profile.sim)

    def _encrypt_necessaries(self, profile, srv_id):
        notv = set(col for col in profile.v
                   if col not in self._get_authz(col, srv_id).v)
        return profile._replace(v=profile.v - notv, e=profile.e | notv)

    def authorize(self, profile, srv_id):
        profile = self._encrypt_necessaries(profile, srv_id)
        return profile if (self._check_v(profile.v | profile.iv, srv_id) and
            self._check_v_or_e(profile.e | profile.ie, srv_id) and
            self._check_sim(profile, srv_id)) else None
