#!/usr/bin/env python

from random import triangular, randrange
from sqlite3 import connect
import argparse
import sys
import os

def generate(db, students):
    conn = connect(db)
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE student (id INTEGER PRIMARY KEY, name TEXT, city TEXT)')
    cursor.executemany('INSERT INTO student VALUES (?, ?, ?)',
        ((s, 's_%d' % s, 'c_%d' % (s % 100))
            for s in xrange(students)))
    conn.commit()

    cursor.execute('CREATE TABLE exam (sid INTEGER, eid INTEGER, grade INTEGER, PRIMARY KEY(sid, eid))')
    cursor.executemany('INSERT INTO exam VALUES (?, ?, ?)',
        ((s, e, int(triangular(18, 30.9, 23)))
            for s in xrange(students)
            for e in xrange(randrange(10))))
    conn.commit()

    cursor.execute('CREATE TABLE city (name TEXT, state TEXT, PRIMARY KEY(name, state))')
    cursor.executemany('INSERT INTO city VALUES (?, ?)',
        (('c_%d' % c, c % 10)
            for c in xrange(students // 100)))
    conn.commit()

    print 'Database %s created with %d students' % (db, students)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db',
        help='Database name', default='test.db')
    parser.add_argument('-n',
        help='Number of students to generate', default=(10 ** 5))
    args = parser.parse_args()
    generate(args.db, args.n)
