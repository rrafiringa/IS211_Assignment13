#!/usr/bin/env python
# -*- Coding: Utf-8 -*-

import sqlite3 as db

class DataBroker(object):
    """
    Data retrieval and entry manager
    """

    def __init__(self, dbfile):
        """
        Constructor
        :param dbfile: (String) Name of database to use
        :param table: (String) Name of target table
        """
        self.dbcon = None
        self.dbcur = None
        self.rows = None
        self.cols = None
        self.cond = None
        self.table = None
        self.dbfile = dbfile
        self.numrows = 0

    def set_table(self, table):
        if self.open(self.dbfile):
            self.table = table
            sql = 'SELECT * FROM ' + self.table + ' LIMIT 1'
            self.dbcur.execute(sql)
            self.fields = tuple(map(lambda x: x[0],
                                    self.dbcur.description))

    def open(self, dbfile):
        """
        Open database
        :param dbfile: (String) Database file path
        :return: (Boolean) False if no connection
        """
        try:
            self.dbcon = db.connect(dbfile)
            self.dbcon.row_factory = db.Row
            self.dbcur = self.dbcon.cursor()
        except db.Error:
            return False
        return True

    def commit(self, query):
        """
        Submit a query to db
        :param query: (String): SQL query
        :return: (Object): Query results
        """
        self.dbcur.execute(query)
        self.numrows = self.dbcur.rowcount
        self.rows = self.dbcur.fetchall()
        return self.rows

    def close(self):
        """
        Close database connection
        """
        return self.dbcon.close()

    def get_data(self, cols=tuple('*'), conditions={}):
        """
        Run a SELECT query against database
        :param cols: (Tuple) Fields to retrieve
        :param conditions: (Dict) Query conditions
        :return:
        """
        first = True
        for col in cols:
            if first:
                self.cols = col
                first = False
            else:
                self.cols += ', ' + col

        sql = 'SELECT ' + self.cols + ' FROM ' + self.table
        for key, value in conditions.items():
            sql += key + ' ' + value
        return self.commit(sql)

    def set_data(self, cols, rows):
        values = fields = ' ('
        first = True
        for col in cols:
            if col in self.fields:
                if first:
                    fields += col
                    values += '?'
                    first = False
                else:
                    fields += ', ' + col
                    values += ', ' + '?'
        fields += ') '
        values += ') '
        sql = "INSERT INTO " + self.table + fields + " VALUES " + values
        return self.dbcon.executemany(sql, rows)

    def del_data(self, conditions={}):
        """
        Delete data from table
        :param conditions: (Dict) Delete conditions
        :return: (Int) Row count
        """
        sql = 'DELETE FROM ' + self.table
        for key, value in conditions.items():
            sql += key + ' ' + value
        return self.dbcon.execute(sql).rowcount


if __name__ == '__main__':
    """
    Driver
    """
    cols = ('first', 'last')
    rows = [('Jack', 'Marin',),
            ('Marian', 'Calhoun',),
            ('Marty', 'Markinson',),
            ('Jor', 'El',)]
    cond = {'WHERE': 'sid = 1'}
    # dbi = DataBroker('hw13.db')
    # dbi.set_table('students')
    # dbi.set_data(cols, rows)


    conn = db.connect('test.db')
    conn.row_factory = db.Row
    cur = conn.cursor()

    res = cur.execute('''INSERT INTO student ('first', 'last') VALUES (?, ?)''', ('John', 'Law'))
    print(res)
    conn.close()
    # dbi.del_data(cond)
    # res = dbi.get_data()
    # for row in res:
    #    print(row)