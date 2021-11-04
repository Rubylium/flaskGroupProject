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
    return link


@app.route("/")
def index():
    rows = GetAllUsersData()
    return render_template("index.html", rows=rows)


@app.route("/clicker")
def clicker():
    data = nbPoints(session["user_id"], )

    priceBoost = getPrice(session["user_id"])

    return render_template("clicker.html", rows=data, price=priceBoost)


@app.route("/click", methods=("POST",))
def click():
    clickPoint(session["user_id"], )
    data = nbPoints(session["user_id"], )

    priceBoost = getPrice(session["user_id"])

    return render_template("clicker.html", rows=data, price=priceBoost)


@app.route("/boost", methods=("POST",))
def boost():
    boostId = request.form["boostId"]
    buyBoostIfPossible(session["user_id"], boostId)
    priceBoost = getPrice(session["user_id"])
    data = nbPoints(session["user_id"], )

    return render_template("clicker.html", rows=data, price=priceBoost)


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
        string = ""
        for v in row:
            string = string + " " + str(v)
        print(string)


def getPriceForStoreId(id_user, store_id):
    priceToReturn = 0
    db = get_db_connection()
    data = db.execute("SELECT * FROM store WHERE id = ?", (store_id)).fetchone()
    basePrice = data["defaultPrice"]
    data = db.execute("SELECT count(*) FROM userBoost WHERE id_user = ? AND id_store = ?", (id_user, store_id)).fetchone()

    if data[0] > 0:
        priceToReturn = (basePrice * data[0]) * 1.25
    else:
        priceToReturn = basePrice

    return priceToReturn

def getPrice(id_user):
    db = get_db_connection()
    data = db.execute("SELECT * FROM store", ())
    dataToSend = []
    for row in data:
        tempData = {}
        tempData["id"] = row[0]
        tempData["libelle"] = row[1]
        tempData["uniqueBoost"] = row[4]
        basePrice = row[3]
        data = db.execute("SELECT count(*) FROM userBoost WHERE id_user = ? AND id_store = ?",(id_user, tempData["id"])).fetchone()
        if data[0] > 0:
            tempData["price"] = (basePrice * data[0]) * 1.25
        else:
            tempData["price"] = basePrice
        tempData["level"] = data[0]
        if tempData["uniqueBoost"] == 1:
            if data[0] == 0:
                dataToSend.insert(0, tempData)
        else:
            dataToSend.insert(0, tempData)
    return dataToSend

def getUserCurrentPointToAdd(id_user):
    db = get_db_connection()
    data = db.execute("SELECT count(*) FROM userBoost WHERE id_user = ?",(id_user,)).fetchone()
    if data[0] > 0:
        rows = db.execute("SELECT userBoost.id_user, store.pointToAdd FROM userBoost INNER JOIN store ON userBoost.id_store = store.id WHERE id_user = ?",(id_user,))
        pointToAdd = 0
        for row in rows:
            pointToAdd = pointToAdd + row[1]
        return pointToAdd
    else:
        return 0


def buyBoostIfPossible(id_user, boostId):
    db = get_db_connection()
    points = int(nbPoints(session["user_id"]))
    priceBoost = getPriceForStoreId(session["user_id"], boostId)
    if points >= priceBoost:
        points = points - priceBoost
        db.execute("INSERT INTO userBoost (id_user, id_store) VALUES (?, ?)", (id_user, boostId))
        db.execute("UPDATE userPoints SET nbPoints = ? WHERE id_user=?", (points, id_user))
        db.commit()


def nbPoints(id_user):
    db = get_db_connection()
    data = db.execute("SELECT nbPoints FROM userPoints WHERE id_user=?", (id_user,)).fetchone()
    return data["nbPoints"]


def clickPoint(id_user):
    db = get_db_connection()
    boostPoints = getUserCurrentPointToAdd(id_user)
    points = int(nbPoints(session["user_id"])) + 1 + boostPoints
    db.execute("UPDATE userPoints SET nbPoints = ? WHERE id_user=?", (points, id_user))
    db.commit()


def CreateNewUser(username, password):
    db = get_db_connection()
    row = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
    if row is None:
        db.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        row = db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()
        db.execute("INSERT INTO userPoints (id_user, nbPoints, boost) VALUES (?, '0', '1')", (str(row["id"])))
        db.commit()

        print("User " + username + " created")
    else:
        print("User already exist, avoid creating user: " + username)


def CreateNewBoost(label, pointToAdd, price, unique):
    db = get_db_connection()
    row = db.execute("SELECT * FROM store WHERE libelle = ?", (label,)).fetchone()
    if row is None:
        db.execute("INSERT INTO store (libelle, pointToAdd, defaultPrice, uniqueBoost) VALUES (?, ?, ?, ?)", (label, pointToAdd, price, unique))
        db.commit()
        print("Boost " + label + " created")
    else:
        print("Boost already exist, avoid creating Boost: " + str(row[0]), str(row[1]), str(row[2]), str(row[3]))

CreateNewUser("Super", "test")
CreateNewUser("Amaleo", "test")
PrintAllUsers()

CreateNewBoost("+1 points", 1, 20, 0)
CreateNewBoost("+5 points", 5, 150, 0)
CreateNewBoost("+20 points", 20, 350, 0)
CreateNewBoost("BelleDelphine", 0, 500, 1)