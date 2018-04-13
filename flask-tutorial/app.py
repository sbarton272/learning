from flask import Flask, render_template
import sqlite3
from flask import g

DATABASE = '/path/to/database.db'

APP = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with APP.app_context():
        db = get_db()
        with APP.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

init_db()

@APP.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@APP.route('/')
def index():
    tables = ['foo']
    return render_template('index.html', tables=tables)

@APP.route('/upload')
def upload():
    return render_template('upload.html')

@APP.route('/query/<table>')
def query(table):
    return render_template('query.html', table=table)
