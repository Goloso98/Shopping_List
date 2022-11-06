from datetime import datetime
from flask import Flask, redirect, render_template, url_for, request
import os
import sqlite3 as sql

app = Flask(__name__, )

DB_FILE = "db/database.db"
DB_SOURCE = "db/schema.sql"

# --- DB ---
def db_init():
    if not os.path.exists(DB_FILE):
        con = sql.connect(DB_FILE)
        cur = con.cursor()
        with open(DB_SOURCE, "r") as f:
            lines = f.readlines()
        script = ''.join(lines)
        cur.executescript(script)
        con.commit()
        cur.close()
        con.close()
    return

def db_conn():
    return sql.connect(DB_FILE,
        detect_types=sql.PARSE_DECLTYPES | sql.PARSE_COLNAMES)

def db_fetchall_star():
    return db_fetchall("SELECT * FROM GROCERIES;");

def db_fetchall(string):
    conn = db_conn()
    rows = conn.execute(string).fetchall()
    conn.close()
    return rows

def db_lastupdate():
    conn = db_conn()
    dt = conn.execute("SELECT TS FROM LASTUPDATE").fetchone()[0]
    conn.close()
    return dt

def db_exec(string):
    conn = db_conn()
    c = conn.cursor()
    c.execute(string)
    conn.commit()
    c.close()
    conn.close()

def db_insert(string, values, timestamp = False):
    """string be like "UPDATE fish SET tank_number = ? WHERE name = ?",
    then the ? values in a tuple"""
    conn = db_conn()
    c = conn.cursor()
    c.execute(string, values)
    if timestamp:
        now = datetime.now()
        c.execute( 'UPDATE LASTUPDATE SET TS=?;', (now,))
    conn.commit()
    c.close()
    conn.close()

# --- run on every request ---
@app.context_processor
def utility_processor():
    def lastupdate():
        dt = db_lastupdate()
        txt = dt.strftime("%d/%m/%Y - %H:%M")
        return txt
    return dict(lastupdate=lastupdate)

# --- VIEWS ---
@app.route('/')
@app.route('/home')
def home():
    in_cart = db_fetchall("SELECT ID, NAME FROM GROCERIES \
        WHERE SHOPPING_LIST AND SHOPPING_CART;")
    out_cart = db_fetchall("SELECT ID, NAME FROM GROCERIES \
        WHERE SHOPPING_LIST AND NOT(SHOPPING_CART);")
    return render_template('home.html', link="home", in_cart=in_cart, out_cart=out_cart)

@app.route('/edit')
def edit():
    in_list = db_fetchall("SELECT ID, NAME, SHOPPING_LIST FROM GROCERIES WHERE SHOPPING_LIST=1;")
    out_list = db_fetchall("SELECT ID, NAME, SHOPPING_LIST FROM GROCERIES WHERE SHOPPING_LIST=0;")
    return render_template('edit.html', link="edit", in_list=in_list, out_list=out_list)

# --- API ---
# --- /edit view
@app.route('/reset')
def reset():
    db_exec( "UPDATE GROCERIES SET SHOPPING_CART=0, SHOPPING_LIST=0;")
    return redirect(url_for("edit"))

@app.route('/add')
def add():
    name = request.args.get("name")
    name = name.capitalize()
    db_insert( "INSERT INTO GROCERIES (NAME) VALUES (?);", \
        (name,), timestamp=True )
    return redirect(url_for("edit"))

@app.route('/delete/<id>')
def delete(id):
    db_insert( 'DELETE FROM GROCERIES WHERE ID=?;', \
        (id,), timestamp=True )
    return redirect(url_for("edit"))

@app.route('/listadd/<id>')
def listadd(id):
    db_insert( 'UPDATE GROCERIES SET SHOPPING_LIST=1 WHERE ID=?;', \
        (id,), timestamp=True )
    return redirect(url_for("edit"))

@app.route('/listdel/<id>')
def listdel(id):
    db_insert( 'UPDATE GROCERIES SET SHOPPING_LIST=0 WHERE ID=?;', \
        (id,), timestamp=True )
    return redirect(url_for("edit"))

# --- /home view
@app.route('/cartadd/<id>')
def cartadd(id):
    db_insert( 'UPDATE GROCERIES SET SHOPPING_CART=1 WHERE ID=?;', \
        (id,) )
    return redirect(url_for("home"))

@app.route('/cartdel/<id>')
def cartdel(id):
    db_insert( 'UPDATE GROCERIES SET SHOPPING_CART=0 WHERE ID=?;', \
        (id,) )
    return redirect(url_for("home"))


db_init()

# if __name__ == "__main__":
#     schema = """CREATE TABLE IF NOT EXISTS GROCERIES (
#         ID            INTEGER PRIMARY KEY AUTOINCREMENT,
#         NAME          TEXT NOT NULL,
#         SHOPPING_LIST BOOLEAN DEFAULT 1,
#         SHOPPING_CART BOOLEAN DEFAULT 0
#         );"""
#     db_exec(schema)
#     # flask run --port=5000
#     app.run(host="0.0.0.0", debug=True)
