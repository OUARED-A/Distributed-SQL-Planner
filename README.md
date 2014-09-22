jupiter-py
==========

Distributed SQL Planner

### Generate a SQLite test database

    $ python db/genpatients.py
    Database test.db created with 100000 patients
    
### Optimize a simple query

    $ ./jupiter.py db/test.db 'SELECT * FROM "hospital"
    === Parsed Tree ===
    1: {u'cumulativeCost': {u'rows': 200000.0, u'cpu': 100001.0, u'io': 300000.0}, u'inputs': [u'0'], u'relOp': u'JdbcToEnumerableConverter', u'cols': [u'patient', u'disease', u'treatment'], u'rowCount': 100000.0, u'cost': {u'rows': 100000.0, u'cpu': 0.0, u'io': 0.0}, u'id': u'1'} 
      0: {u'cumulativeCost': {u'rows': 100000.0, u'cpu': 100001.0, u'io': 300000.0}, u'inputs': [], u'relOp': u'JdbcTableScan', u'cols': [u'patient', u'disease', u'treatment'], u'rowCount': 100000.0, u'cost': {u'rows': 100000.0, u'cpu': 100001.0, u'io': 300000.0}, u'table': [u'main', u'hospital'], u'id': u'0'} 
    
    === Plans ===
    [Plan cost=420.001 {H:400.001, H->*:20} nodes={0:H, 1:CL}]
    
    === Best Plan ===
    [Plan cost=420.001 {H:400.001, H->*:20} nodes={0:H, 1:CL}]
    1CL: {u'cumulativeCost': {u'rows': 200000.0, u'cpu': 100001.0, u'io': 300000.0}, u'inputs': [u'0'], u'relOp': u'JdbcToEnumerableConverter', u'cols': [u'patient', u'disease', u'treatment'], u'rowCount': 100000.0, u'cost': {u'rows': 100000.0, u'cpu': 0.0, u'io': 0.0}, u'id': u'1'} Profile(v=set([u'patient', u'disease', u'treatment']), e=set([]), iv=set([]), ie=set([]), sim=[])
      0H: {u'cumulativeCost': {u'rows': 100000.0, u'cpu': 100001.0, u'io': 300000.0}, u'inputs': [], u'relOp': u'JdbcTableScan', u'cols': [u'patient', u'disease', u'treatment'], u'rowCount': 100000.0, u'cost': {u'rows': 100000.0, u'cpu': 100001.0, u'io': 300000.0}, u'table': [u'main', u'hospital'], u'id': u'0'} Profile(v=set([u'patient', u'disease', u'treatment']), e=set([]), iv=set([]), ie=set([]), sim=[])
      

### Configure the servers

The configuration file is located at `config/servers`. The configuration define for each server the tables, the cost for cpu, io, network-in and network-out and the authorization that other server have on each table.
There must be a *server* named `CL` which is the *client* on which the root of the relational algebra tree is executed.

    [
      {
        "id": "CL",
        "cpu": 0.002,
        "io": 0.002,
        "netin": 0.0,
        "netout": 0.0,
        "tables": []
      },
      {
        "id": "H",
        "cpu": 0.001,
        "io": 0.001,
        "netin": 0.0002,
        "netout": 0.0002,
        "tables": [
          {
            "name": "hospital",
            "columns": ["patient", "disease", "treatment"],
            "authorizations": [
              {
                "server": "H",
                "v": ["patient", "disease", "treatment"],
                "e": []
              },
              {
                "server": "I",
                "v": ["patient"],
                "e": ["disease", "treatment"]
              },
              {
                "server": "D",
                "v": [],
                "e": ["patient", "disease", "treatment"]
              },
              {
                "server": "CL",
                "v": ["patient", "disease", "treatment"],
                "e": []
              },
              {
                "server": "",
                "v": [],
                "e": ["patient", "disease", "treatment"]
              }
            ]
          }
        ]
      },
      {
        "id": "I",
        "cpu": 0.0012,
        "io": 0.0012,
        "netin": 0.0005,
        "netout": 0.0005,
        "tables": [
          {
            "name": "insurance",
            "columns": ["customer", "premium"],
            "authorizations": [
              {
                "server": "H",
                "v": [],
                "e": ["customer", "premium"]
              },
              {
                "server": "I",
                "v": ["customer", "premium"],
                "e": []
              },
              {
                "server": "D",
                "v": [],
                "e": ["customer", "premium"]
              },
              {
                "server": "CL",
                "v": ["customer", "premium"],
                "e": []
              },
              {
                "server": "",
                "v": [],
                "e": []
              }
            ]
          }
        ]
      },
      {
        "id": "D",
        "cpu": 0.002,
        "io": 0.0008,
        "netin": 0.0005,
        "netout": 0.0005,
        "tables": [
          {
            "name": "dhs",
            "columns": ["SSN", "employer", "salary"],
            "authorizations": [
              {
                "server": "H",
                "v": [],
                "e": ["SSN", "employer", "salary"]
              },
              {
                "server": "I",
                "v": ["SSN", "employer"],
                "e": ["salary"]
              },
              {
                "server": "D",
                "v": ["SSN", "employer", "salary"],
                "e": []
              },
              {
                "server": "CL",
                "v": ["SSN", "employer", "salary"],
                "e": []
              },
              {
                "server": "",
                "v": [],
                "e": ["SSN", "salary"]
              }
            ]
          }
        ]
      }
    ]

### Other information

* All the names that are not uppercase must be enclosed in quotes.
* The names of the columns must be unique.
* It works with python 2.x
* It works with projections, selections and aggregates.
* It uses `optiq` as planner.


### Examples

    ./jupiter.py db/test.db 'SELECT "patient", "disease", "premium" FROM "hospital" AS "H" JOIN "insurance" AS "I" ON "H"."patient" = "I"."customer"'
    
    ./jupiter.py db/test.db 'SELECT "patient", "disease", "premium" FROM "hospital" AS "H" JOIN "insurance" AS "I" ON "H"."patient" = "I"."customer" WHERE "H"."patient" > 1000'
