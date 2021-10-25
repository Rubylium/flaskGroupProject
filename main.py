from flask import Flask, render_template, session, request, flash, url_for
from markupsafe import escape
import sqlite3
from flask import g
from werkzeug.security import check_password_hash
from werkzeug.utils import redirect

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def get_db_connection():
    link = sqlite3.connect("flaskProject.db")
    link.row_factory = sqlite3.Row
    db = link.cursor()
    return db


def GetConnDb():
    conn = sqlite3.connect("flaskProject.db")
    return conn


@app.route("/")
def index():
    rows = GetAllUsersData()
    return render_template("index.html", rows=rows)


@app.route("/clicker")
def clicker():
    data = nbPoints(session["user_id"],)
    return render_template("clicker.html", rows=data[0])


@app.route("/<name>")
def hello(name):
    return f"Sorry, the page {escape(name)} do not exist!"


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]
        db = get_db_connection()
        error = None
        user = db.execute("SELECT * FROM user WHERE username = ?", (user,)).fetchone()

        if user is None:
            error = "Incorrect username."
        # elif not check_password_hash(user["password"], password):
        #    error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("clicker"))
        else:
            flash(error)

    return render_template("index.html")


@app.route('/logout', methods=("POST",))
def logout():
    session.clear()
    return redirect(url_for('login'))


# DB Connection + creation of tables
def InitDatabse():
    cursor = get_db_connection()
    sql_file = open("schema.sql")
    sql_as_string = sql_file.read()
    cursor.executescript(sql_as_string)
    print("Database init done!")


InitDatabse()


def GetAllUsersData():
    db = get_db_connection()
    rows = db.execute("SELECT * FROM user INNER JOIN userPoints ON user.id = userPoints.id_user").fetchall()
    return rows


def PrintAllUsers():
    print("Showing all users")

    cursor = get_db_connection()
    for row in cursor.execute("SELECT * FROM user"):
        print(row)


def nbPoints(id_user):
    cursor = get_db_connection()
    data = cursor.execute("SELECT nbPoints FROM userPoints WHERE id_user=?", (id_user,)).fetchone()
    return data


def clickPoint(id_user):
    cursor = get_db_connection()
    points = nbPoints(session["user_id"]) + 1
    data = cursor.execute("UPDATE userPoints SET userPoints = ? WHERE id_user=?", (points, id_user))
    return data


def close_db():
    db = g.pop("db", None)
    if db is not None:
        db.close()


def CreateNewUser(username, password):
    db = get_db_connection()
    conn = GetConnDb()
    row = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
    if row is None:
        db.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
        conn.commit()

        row = db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()

        db.execute("INSERT INTO userPoints (id_user, nbPoints) VALUES (?, '0')", (str(row["id"])))
        conn.commit()

        print("User " + username + " created")
    else:
        print("User already exist, avoid creating user: " + username)


CreateNewUser("Super", "test")
PrintAllUsers()
