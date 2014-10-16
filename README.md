jupiter-py
==========

Distributed SQL Planner based on [`optiq`](https://github.com/apache/incubator-optiq) as planner and python 2.7.


### Usage

    usage: jupiter.py [-h] [-n] [-j] SERVERS DB SQL
    
    Use Optiq to get a relational plan from SQL statement.
    
    positional arguments:
      SERVERS       Servers configuration file
      DB            SQLite database to use as schema source
      SQL           SQL query (quote it as a single string)
    
    optional arguments:
      -h, --help    show this help message and exit
      -n, --no-opt  Convert SQL to a relational plan but do not optimize
      -j, --json    Output the result as JSON

### Generate a SQLite test database

The default configuration in `config/servers` uses a database of patients, that can be generated:

    $ python db/genpatients.py
    Database test.db created with 100000 patients

    
### Optimize a simple query

In order to optimize a query, execute `jupiter.py` using the name of the database that will be used to read the schema, and the query you want to optimize as parameters.

    $ ./jupiter.py config/servers test.db 'SELECT * FROM hospital'
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
The server named `*` is used as a default when a specific authorization for a server is not found.

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
                "server": "*",
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
                "server": "*",
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
                "server": "*",
                "v": [],
                "e": ["SSN", "salary"]
              }
            ]
          }
        ]
      }
    ]


### Other information

* The names of the columns must be unique.
* It works with projections, single selections and aggregates.

Jupiter invokes the optiq planner to generate a plan that is optimal on a single machine, then jupiter analyzes which servers are allowed to execute the every relational node and it select the combination that satisfies the authorization constraints while minimizing the total cost (based on the configuration).


### Examples

* Join two tables and project columns:

        ./jupiter.py config/servers test.db 'SELECT patient, disease, premium FROM hospital AS H JOIN insurance AS I ON H.patient = I.customer'

* Join two tables, project columns and filter the results:

        ./jupiter.py config/servers test.db 'SELECT patient, disease, premium FROM hospital AS H JOIN insurance AS I ON H.patient = I.customer WHERE H.patient > 1000'

### TPC-H database

You can generate a SQLite TPC-H database. To do that check the README in the tpch folder.
