import click
from flask import Flask
from flask.cli import with_appcontext
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


conn = sqlite3.connect("flaskProject.db")
print("Opened database successfully")


def get_db_connection():
    conn = sqlite3.connect("flaskProject.db")
    conn.row_factory = sqlite3.Row
    return conn


cur = get_db_connection()

test = cur.execute("SELECT * FROM users")
print(test)


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db_connection()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database')
