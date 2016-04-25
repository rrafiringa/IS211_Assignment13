#!/usr/bin/env python
# -*- Coding: Utf-8 -*-

"""
IS211 Assignment 13: Flask web dev part II
"""

from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3


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
            error = '<strong>Error: </strong>Wrong credentials, please try again.'
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


@app.route('/results/add')
def add_results():
    pass


@app.route('/student/<id>')
def get_student_results(id):
    # Results or msg 'No result'
    pass


def dbconnect():
    return sqlite3.connect(app.database)


def insert(table, field=(), values=()):
    cur = g.db.cursor()
    query = 'INSERT INTO {} ({}) VALUES ({})'.format(
        table,
        ', '.join(fields),
        ', '.join(['?'] * len(values))
    )
    cur.execute(query, values)
    g.db.commit()
    rid = cur.lastrowid
    cur.close()
    return rid


if __name__ == '__main__':
    app.run(debug=True)

