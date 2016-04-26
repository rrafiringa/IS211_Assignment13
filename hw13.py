#!/usr/bin/env python
# -*- Coding: Utf-8 -*-

"""
IS211 Assignment 13: Flask web dev part II
"""

import sqlite3

from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)

app.database = 'hw13.db'


@app.route('/')
def start():
    """
    First page
    """
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login form processing
    On success: go to /dashboard
    On fail: Go to /login with error
    """
    error = None
    if request.method == 'POST':
        user = request.form['user'].strip()
        pwd = request.form['pass'].strip()
        if user == 'admin' and pwd == 'password':
            return redirect('/dashboard')
        else:
            error = 'Wrong credentials, please try again.'
    return render_template('login.xhtml', error=error)


@app.route('/dashboard')
def dashboard():
    """
    Teacher dashboard
    """
    g.db = dbconnect()
    g.db.row_factory = sqlite3.Row
    squery = "SELECT * FROM students"
    students = g.db.execute(squery)
    qquery = "SELECT * FROM quizzes"
    quizzes = g.db.execute(qquery)
    return render_template('dashboard.xhtml', students=students, quizzes=quizzes)


@app.route('/student/add', methods=['POST'])
def add_student():
    if request.method == 'POST':
        cols = ('first', 'last')
        row = (
            request.form['first'],
            request.form['last'])
        g.db = dbconnect()
        insert('students', cols, row)
        return redirect(url_for('dashboard'))


@app.route('/quizz/add', methods=['GET', 'POST'])
def add_quizz():
    if request.method == 'POST':
        cols = ('date', 'subj', 'numq')
        values = (
            request.form['date'],
            request.form['subj'],
            request.form['numq']
        )
        g.db = dbconnect()
        insert('quizzes', cols, values)
        return redirect(url_for('dashboard'))


@app.route('/results/add', methods=['GET', 'POST'])
def add_results():
    queries = {'s': "SELECT sid, first || ' ' || last AS student "
                    "FROM students",
               'q': "SELECT qid, date || ' - ' || subj AS quiz "
                    "FROM quizzes",
               'd': "SELECT s.first || ' ' || s.last as student, "
                    "q. subj, q.date, r.score, r.rid FROM results AS r "
                    "LEFT JOIN students AS s ON r.sid = s.sid "
                    "LEFT JOIN quizzes AS q ON r.qid = q.qid "
                    "ORDER BY q.date DESC"}

    results = {'s': None,
               'q': None,
               'd': None}

    if request.method == 'POST':
        cols = ('sid', 'qid', 'score')
        row = (request.form['sid'],
               request.form['qid'],
               request.form['score'])
        g.db = dbconnect()
        insert('results', cols, row)

    for (idx, query) in queries.items():
        g.db = dbconnect()
        g.db.row_factory = sqlite3.Row
        cur = g.db.cursor()
        res = cur.execute(query)
        rows = res.fetchall()
        results[idx] = rows
        cur.close()

    return render_template('score.xhtml',
                           students=results['s'],
                           quizzes=results['q'],
                           display=results['d'])


@app.route('/results/delete/<int:rid>')
def del_result(rid):
    g.db = dbconnect()
    msg = delete('results', 'rid', rid)
    return redirect(url_for('add_results', message=msg))


@app.route('/student/<int:sid>')
def get_results(sid):
    # Results or msg 'No result'
    error = None
    query = 'SELECT * FROM results AS r LEFT JOIN quizzes AS q ON r.qid = q.qid WHERE r.sid = {}'.format(sid)
    g.db = dbconnect()
    g.db.row_factory = sqlite3.Row
    rows = g.db.execute(query).fetchall()
    if len(rows) <= 0:
        error = 'No Result'
    return render_template('results.xhtml', rows=rows, error=error)


def dbconnect():
    """
    Connect to sqlite database
    :return: (Object) sqlite3 database connection object
    """
    return sqlite3.connect(app.database)


def insert(table, fields=(), values=()):
    """
    Insert record into table
    :param table: (String) Table name
    :param fields: (Tuple) List of fields
    :param values: (Tuple) List of values
    :return: (Int) Affected rows
    """
    cur = g.db.cursor()
    query = 'INSERT INTO {} ({}) VALUES ({})'.format(
        table, ', '.join(fields),
        ', '.join(['?'] * len(values)))
    cur.execute(query, values)
    g.db.commit()
    rid = cur.lastrowid
    cur.close()
    return rid


def delete(table, colname=None, colvalue=None):
    """
    Deletes item from table
    :param table: (String) - Table name
    :param colname: (String) - Optional column name
    :param colvalue: (Mixed) - Value
    """
    cur = g.db.cursor()
    cond = None
    if colname is not None and colvalue is not None:
        cond = ' WHERE {} = {}'.format(colname, colvalue)
    query = 'DELETE FROM {}'.format(table) + cond
    cur.execute(query)
    g.db.commit()
    cur.close()
    return query


if __name__ == '__main__':
    app.run(debug=True)
