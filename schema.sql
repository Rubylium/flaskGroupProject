CREATE TABLE IF EXISTS user;
CREATE TABLE IF EXISTS userPoints;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE userPoints(
    id INTEGER PRIMARY KEY,
    nbPoints INTEGER DEFAULT '0',
    FOREIGN KEY (id_user) REFERENCES user (id)
);