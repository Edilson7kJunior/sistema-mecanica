from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def db():
    return sqlite3.connect("database.db")

def init_db():

    conn = db()
    c = conn.cursor()

    # peças usadas na ordem

    c.execute("""
    CREATE TABLE IF NOT EXISTS ordem_pecas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ordem_id INTEGER,
    peca_id INTEGER,
    quantidade INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS clientes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        telefone TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS motos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        modelo TEXT,
        placa TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS estoque(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        quantidade INTEGER,
        preco REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS ordens(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT,
        placa TEXT,
        modelo TEXT,
        servico TEXT,
        status TEXT,
        pago TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


@app.route("/")
def dashboard():

    conn = db()
    c = conn.cursor()

    clientes = c.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    estoque = c.execute("SELECT COUNT(*) FROM estoque").fetchone()[0]
    ordens = c.execute("SELECT COUNT(*) FROM ordens WHERE status='Aberta'").fetchone()[0]

    return render_template("dashboard.html",
                           clientes=clientes,
                           estoque=estoque,
                           ordens=ordens)


@app.route("/clientes", methods=["GET","POST"])
def clientes():

    conn = db()
    c = conn.cursor()

    if request.method == "POST":

        nome = request.form["nome"]
        telefone = request.form["telefone"]

        c.execute("INSERT INTO clientes(nome,telefone) VALUES(?,?)",
                  (nome,telefone))

        conn.commit()

    lista = c.execute("SELECT * FROM clientes").fetchall()

    return render_template("clientes.html",clientes=lista)


@app.route("/estoque", methods=["GET","POST"])
def estoque():

    conn = db()
    c = conn.cursor()

    if request.method == "POST":

        nome = request.form["nome"]
        quantidade = int(request.form["quantidade"])
        preco = request.form["preco"]
        acao = request.form["acao"]

        peca = c.execute(
            "SELECT * FROM estoque WHERE nome=?",
            (nome,)
        ).fetchone()

        if peca:

            if acao == "entrada":

                c.execute("""
                UPDATE estoque
                SET quantidade = quantidade + ?
                WHERE nome = ?
                """,(quantidade,nome))

            else:

                c.execute("""
                UPDATE estoque
                SET quantidade = quantidade - ?
                WHERE nome = ?
                """,(quantidade,nome))

        else:

            c.execute("""
            INSERT INTO estoque(nome,quantidade,preco)
            VALUES(?,?,?)
            """,(nome,quantidade,preco))

        conn.commit()

    pecas = c.execute("SELECT * FROM estoque").fetchall()

    return render_template("estoque.html",pecas=pecas)


@app.route("/ordens", methods=["GET","POST"])
def ordens():

    conn = db()
    c = conn.cursor()

    if request.method == "POST":

        cliente = request.form["cliente"]
        placa = request.form["placa"]
        modelo = request.form["modelo"]
        servico = request.form["servico"]
        pago = request.form["pago"]

        c.execute("""
        INSERT INTO ordens(cliente,placa,modelo,servico,status,pago)
        VALUES(?,?,?,?,?,?)
        """,(cliente,placa,modelo,servico,"Aberta",pago))

        conn.commit()

    lista = c.execute("SELECT * FROM ordens").fetchall()

    pecas = c.execute("SELECT * FROM estoque").fetchall()

    return render_template("ordens.html",
                           ordens=lista,
                           pecas=pecas)


@app.route("/status", methods=["POST"])
def status():

    conn = db()
    c = conn.cursor()

    ordem_id = request.form["ordem_id"]
    status = request.form["status"]

    c.execute("""
    UPDATE ordens
    SET status = ?
    WHERE id = ?
    """,(status,ordem_id))

    conn.commit()

    return redirect("/ordens")

@app.route("/add_peca", methods=["POST"])
def add_peca():

    conn = db()
    c = conn.cursor()

    ordem_id = request.form["ordem_id"]
    peca_id = request.form["peca_id"]
    quantidade = int(request.form["quantidade"])

    # salvar peça usada

    c.execute("""
    INSERT INTO ordem_pecas(ordem_id,peca_id,quantidade)
    VALUES(?,?,?)
    """,(ordem_id,peca_id,quantidade))

    # baixar do estoque

    c.execute("""
    UPDATE estoque
    SET quantidade = quantidade - ?
    WHERE id = ?
    """,(quantidade,peca_id))

    conn.commit()

    return redirect("/ordens")


@app.route("/consulta", methods=["GET","POST"])
def consulta():

    conn = db()
    c = conn.cursor()

    resultado = []

    if request.method == "POST":

        busca = request.form["busca"]

        resultado = c.execute("""
        SELECT * FROM ordens
        WHERE cliente LIKE ?
        OR placa LIKE ?
        OR modelo LIKE ?
        """,(f"%{busca}%",f"%{busca}%",f"%{busca}%")).fetchall()

    return render_template("consulta.html",resultado=resultado)


app.run(debug=True)
