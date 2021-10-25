from flask import Flask, render_template, session, request, flash, url_for
from markupsafe import escape
import sqlite3
from flask import g
from werkzeug.security import check_password_hash
from werkzeug.utils import redirect

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Routes


@app.route("/")
def index():
    rows = GetAllUsersData()
    return render_template("index.html", rows=rows)


@app.route("/<name>")
def hello(name):
    return f"Sorry, the page {escape(name)} do not exist!"


@app.route("/", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]
        db = get_db_connection()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (user,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("template/clicker.html")


# DB Connection + creation of tables
conn = sqlite3.connect("flaskProject.db")
print("Opened database successfully")
cursor = conn.cursor()
sql_file = open("schema.sql")

sql_file = open("schema.sql")
sql_as_string = sql_file.read()
cursor.executescript(sql_as_string)


def GetAllUsersData():
    db = get_db_connection()
    rows = db.execute("SELECT * FROM user INNER JOIN userPoints ON user.id = userPoints.id_user").fetchall()
    return rows


def PrintAllUsers():
    print("Showing all users")
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



