from flask import Flask, redirect, render_template, url_for, request
import sqlite3

app = Flask(__name__, )

DB_FILE = "database.db"

# --- DB ---
def db_fetchall_star():
    return db_fetchall("SELECT * FROM GROCERIES;");

def db_fetchall(string):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    rows = c.execute(string).fetchall()
    conn.close()
    return rows

def db_exec(string):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(string)
    conn.commit()
    conn.close()

def db_insert(string, values):
    """string be like "UPDATE fish SET tank_number = ? WHERE name = ?",
    then the ? values in a tuple"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(string, values)
    conn.commit()
    conn.close()

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
        (name,) )
    return redirect(url_for("edit"))

@app.route('/delete/<id>')
def delete(id):
    db_insert( 'DELETE FROM GROCERIES WHERE ID=?;', \
        (id,) )
    return redirect(url_for("edit"))

@app.route('/listadd/<id>')
def listadd(id):
    db_insert( 'UPDATE GROCERIES SET SHOPPING_LIST=1 WHERE ID=?;', \
        (id,) )
    return redirect(url_for("edit"))

@app.route('/listdel/<id>')
def listdel(id):
    db_insert( 'UPDATE GROCERIES SET SHOPPING_LIST=0 WHERE ID=?;', \
        (id,) )
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


schema = """CREATE TABLE IF NOT EXISTS GROCERIES (
    ID            INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME          TEXT NOT NULL,
    SHOPPING_LIST BOOLEAN DEFAULT 1,
    SHOPPING_CART BOOLEAN DEFAULT 0
    );"""
db_exec(schema)

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