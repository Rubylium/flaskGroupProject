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


def get_db_connection():
    conn = sqlite3.connect('flaskProject.db')
    conn.row_factory = sqlite3.Row
    return conn


cur = get_db_connection()

test = cur.execute("SELECT * FROM users")
print(test)


def close_db(e = None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
