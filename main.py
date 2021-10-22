import con as con
from flask import Flask
from markupsafe import escape
import sqlite3
from flask import current_app, g

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/<name>")
def hello(name):
    return f"Sorry, the page {escape(name)} do not exist!"


conn = sqlite3.connect('flaskProject.db')
print("Opened database successfully")

cur = con.cursor()


def get_db():
    if 'flaskProject' not in g:
        g.db = sqlite3.connect(
            current_app.config['flaskProject'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
