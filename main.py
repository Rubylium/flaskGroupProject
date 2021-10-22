import click
from flask import Flask, render_template
from flask.cli import with_appcontext
from markupsafe import escape
import sqlite3
from flask import current_app, g

app = Flask(__name__)

# Routes

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<name>")
def hello(name):
    return f"Sorry, the page {escape(name)} do not exist!"


# DB Connection + creation of tables
conn = sqlite3.connect("flaskProject.db")
print("Opened database successfully")
cursor = conn.cursor()

sql_file=open("schema.sql")
sql_as_string = sql_file.read()
cursor.executescript(sql_as_string)

for row in cursor.execute("SELECT * FROM user"):
    print(row)


def get_db_connection():
    conn = sqlite3.connect("flaskProject.db")
    conn.row_factory = sqlite3.Row
    return conn


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()



