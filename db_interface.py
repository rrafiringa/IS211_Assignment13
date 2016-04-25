#!/usr/bin/env python
# -*- Coding: Utf-8 -*-

"""
Interface with sqlite database
"""
import sqlite3 as db


class Record(object):
    def __init__(self, fields, values=None):
        """
        Record object constructor
        :param fields: (Sequence) Tuple of field names
        :param values: (Optional) Tuple of field values
        """
        self.row = None
        self.fields = tuple(fields)
        self.values = None
        if values is not None:
            self.set_record(values)

    def set_record(self, row):
        """
        Set fields and associated values
        :param row: (Sequence) List of field values
        :return: (Boolean) True if record is created
        """
        if len(self.fields) != len(row):
            return False
        self.values = tuple(row)
        self.row = dict(zip(self.fields, self.values))
        return True

    def get_field(self, key):
        """
        Get value of field in record.
        :param key:
        :return: (Mixed) Value of field
        """
        return self.row[key]

    def set_field(self, key, data):
        """
        Set value of field
        :param key: (Mixed) Key of field
        :param data: (Mixed) Value of field
        """
        self.row[key] = data

    def get_record(self):
        """
        Returns the row
        :return: (Dict)
        """
        return self.row

    def html_table(self):
        """
        Output as html table row
        :return: (String) HTML
        """
        out = '\t<tbody>\n'
        out += self.html_rows()
        out += '\t</tbody>\n'
        return out

    def html_rows(self):
        """
        Outputs only <tr> tags
        :return: HTML
        """
        out = '\t\t<tr>\n'
        for col in self.fields:
            out += '\t\t\t<td>'
            out += str(self.row[col])
            out += '</td>\n'
        out += '\t\t</tr>\n'
        return out


class RecordSet(object):
    """
    Recordset object
    """
    def __init__(self, fields):
        """
        Constructor
        :param fields: (Sequence) Field names
        """
        self.rows = []
        self.fields = tuple(fields)

    def count(self):
        """
        Get number of rows
        :return: (Int) Row count
        """
        return len(self.rows)

    def add_row(self, row):
        """
        Add a row to recordset
        :param row: (Tuple) Row to add
        """
        self.rows.append(Record(self.fields, row))

    def get_row(self, index):
        """
        Retrieve a row at index from dataset
        :param index: (Int) Index of row to retrieve
        """
        return self.rows[index]

    def update_row(self, index, row):
        """
        Update a row in dataset
        :param index: (Int) Target row index
        :param row: (Tuple) Row data
        :return: (Boolean) True if update is successful
        """
        try:
            self.rows[index] = Record(self.fields, row)
        except IndexError:
            return False
        return True

    def copy_db(self, db_resultset):
        """
        Build from DB query resultset
        :param db_resultset (Object) DB result set
        """
        for row in db_resultset:
            self.add_row(row)

    def copy(self, dataset):
        """
        Deep copy of datasets
        :param dataset: (Object) RecordSet object
        """
        self.fields = dataset.fields
        for row in dataset.rows:
            self.rows.append(row)

    def del_row(self, index):
        """
        Delete a row from dataset
        :param index: (Int) Index of row to delete
        :return (Mixed) Row or False
        """
        try:
            return self.rows.pop(index)
        except IndexError:
            return False

    def html_table(self, caption=None, attrs=None):
        """
        Output dataset as HTML table
        :param caption: (String) Optional table caption
        :param attrs: (String) Optional table attributes
        :return: (String) HTML table code
        """
        out = '<table>\n'
        if attrs is not None:
            out = '<table ' + attrs + '>'
        if caption is not None:
            out += '\t<caption>' + caption + '</caption>\n'
        out += '\t<thead>\n'
        out += '\t\t<tr>\n'
        for col in self.fields:
            out += '\t\t\t<td>' + str(col) + '</td>\n'
        out += '\t\t</tr>\n'
        out += '\t</thead>\n'
        for row in self.rows:
            out += row.html_table()
        out += '</table>'
        return out


class DataBroker(object):
    """
    Data retrieval and entry manager
    """

    def __init__(self, dbfile, table):
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
        self.numrows = 0
        self.open(dbfile)
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

    def get_data(self, fields=None, conditions=None):
        """
        Get values from table:
        :param fields: (Tuple) Fields to retrieve
        :param conditions: (Dict) Query conditions
        :return: (RecordSet) List of Record objects
        """
        sql = 'SELECT '
        first = True

        self.cond = ''

        self.fields = fields

        self.cols = '*'

        for col in self.fields:
            if first:
                self.cols = col
            self.cols += ', ' + col

        if conditions is not None:
            for key, val in conditions:
                self.cond += key + ' ' + val

        data = RecordSet(self.fields)
        sql += self.cols + ' FROM ' + self.table + self.cond
        data.copy_db(self.commit(sql))
        return data

    def set_data(self, record):
        """
        Insert values in table
        :param record: (Record) Record object
        :return: (Object) Query results
        """
        sql = 'INSERT INTO ' + self.table
        first = True
        cols = None
        data = None
        for field in record.fields:
            if first:
                cols = field
                data = record.get_value(field)
            cols += ', ' + field
            data += ', ' + record.get_value(field)
        sql += '(' + cols + ') values (' + data + ')'
        return self.commit(sql)

    def update_data(self, dataset, specs):
        pass

    def del_data(self, specs):
        """
        Delete values from table
        :param specs: (Dict) Field name, value pair
        """
        for field, value in specs.iter_items():
            sql = 'delete from ' + self.table + \
                  ' where ' + field + ' = ' + value
            return self.commit(sql)


if __name__ == '__main__':
    """ Driver """
    broker = DataBroker('hw13.db', 'students')
    students = RecordSet(broker.fields)
    students.copy(broker.get_data(('first', 'last'), {'WHERE': 'sid = 0'}))
    print(students.html_table())
