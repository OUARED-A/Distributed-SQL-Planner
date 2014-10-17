#!/usr/bin/env python

from random import triangular
from sqlite3 import connect
import argparse
import sys
import os

def generate(db, patients):
    conn = connect(db)
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE hospital (patient INTEGER PRIMARY KEY, disease TEXT, treatment TEXT)')
    cursor.executemany('INSERT INTO hospital VALUES (?, ?, ?)',
        ((p, 'd_%d' % (p % 100), 't_%d' % (p % 50))
            for p in xrange(patients)))
    conn.commit()

    cursor.execute('CREATE TABLE insurance (customer INTEGER PRIMARY KEY, premium INTEGER)')
    cursor.executemany('INSERT INTO insurance VALUES (?, ?)',
        ((p, triangular(200, 2000, 500))
          for p in xrange(patients)))
    conn.commit()

    cursor.execute('CREATE TABLE dhs (SSN INTEGER, employer TEXT, salary INTEGER, PRIMARY KEY(SSN, employer))')
    cursor.executemany('INSERT INTO dhs VALUES (?, ?, ?)',
        ((p, 'e_%d' % (p % 100), triangular(100, 5000, 1000))
            for p in xrange(3 * patients // 2)))
    conn.commit()

    print 'Database %s created with %d patients' % (db, patients)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db',
        help='Database name', default='test.db')
    parser.add_argument('-n',
        help='Number of patients to generate', default=(10 ** 5))
    args = parser.parse_args()
    generate(args.db, args.n)
