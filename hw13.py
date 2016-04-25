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
        rows = (request.form[cols[0]], request.form[cols[1]])

        redirect(url_for('dashboard'))


@app.route('/quizz/add', methods=['POST'])
def add_quizz():
    redirect(url_for('dashboard'))


@app.route('/results/add')
def add_results():
    pass


@app.route('/student/<id>')
def get_student_results(id):
    # Results or msg 'No result'
    pass

def dbconnect():
    return sqlite3.connect(app.database)


if __name__ == '__main__':
    app.run(debug=True)

