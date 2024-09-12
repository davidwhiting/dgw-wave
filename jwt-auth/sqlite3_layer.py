"""Basic SQLite3 interface to store and retrieve user credentials"""
import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None;
    try:
        #conn = sqlite3.connect(':memory:') # creates a memory-only database for this example
        conn = sqlite3.connect('test.db') # creates a memory-only database for this example
        return conn
    except Error as e:
        print(e)

def create_table(conn):
    try:
        sql_create_credentials_table = """ CREATE TABLE IF NOT EXISTS credentials (
                                                user TEXT PRIMARY KEY,
                                                hashed_pw TEXT NOT NULL
                                            ); """
        c = conn.cursor()
        c.execute(sql_create_credentials_table)
    except Error as e:
        print(e)

def create_user(conn, user: str, hashed_pw: str):
    try:
        sql = ''' INSERT INTO credentials(user,hashed_pw)
                  VALUES(?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (user, hashed_pw))
        conn.commit()
        return True
    except Error as e:
        print(e)
        return False

def has_user(conn, user: str):
    cur = conn.cursor()
    cur.execute("SELECT * FROM credentials WHERE user=?", (user,))

    rows = cur.fetchall()

    return len(rows) != 0

def get_hashed_pw(conn, user: str):
    cur = conn.cursor()
    cur.execute("SELECT hashed_pw FROM credentials WHERE user=?", (user,))

    rows = cur.fetchall()

    if len(rows) == 0:
        print("Could not find user", user)
        return None
    elif len(rows) > 1:
        print("More than 1 user found:", user)
        return None
    else:
        return rows[0][0]

# create a database connection
conn = create_connection()

# create table
if conn is not None:
    create_table(conn)
else:
    print("Error! cannot create the database connection.")

