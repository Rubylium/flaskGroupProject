from flask import Flask
from markupsafe import escape
import sqlite3

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/<name>")
def hello(name):
    return f"Sorry, the page {escape(name)} do not exist!"


conn = sqlite3.connect('flaskProject.db')
print("Opened database successfully")