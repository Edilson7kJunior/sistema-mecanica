from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)

# =============================
# BANCO
# =============================

def db():
    return sqlite3.connect("mecanica.db")


def init():
    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS pecas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        quantidade INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS servicos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT,
        placa TEXT,
        descricao TEXT,
        pago TEXT
    )
    """)

    conn.commit()
    conn.close()

init()

# =============================
# TEMPLATE UI
# =============================

layout = """
<!DOCTYPE html>
<html>
<head>

<title>Sistema Oficina</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
body{
background:#f4f6f9;
}

.card{
border:none;
border-radius:15px;
box-shadow:0 5px 15px rgba(0,0,0,0.1);
}

.header{
background:#111;
color:white;
padding:20px;
border-radius:0 0 20px 20px;
margin-bottom:30px;
}

</style>

</head>
<body>

<div class="header">
<div class="container">
<h2>🏍 Sistema de Gestão de Mecânica</h2>
</div>
</div>

<div class="container">

<div class="row g-4">

<div class="col-md-6">
<div class="card p-4">
<h4>📦 Cadastrar Peça</h4>

<form method="post" action="/add_peca">
<input class="form-control mb-2" name="nome" placeholder="Nome da peça">
<input class="form-control mb-2" name="quantidade" type="number" placeholder="Quantidade">

<button class="btn btn-dark w-100">Salvar</button>
</form>

</div>
</div>


<div class="col-md-6">
<div class="card p-4">
<h4>🔧 Nova Ordem de Serviço</h4>

<form method="post" action="/add_servico">

<input class="form-control mb-2" name="cliente" placeholder="Cliente">
<input class="form-control mb-2" name="placa" placeholder="Placa da Moto">
<input class="form-control mb-2" name="descricao" placeholder="Serviço realizado">

<select class="form-control mb-2" name="pago">
<option>Não</option>
<option>Sim</option>
</select>

<button class="btn btn-success w-100">Registrar Serviço</button>

</form>

</div>
</div>

</div>


<div class="row mt-4">

<div class="col-md-6">
<div class="card p-4">
<h4>📦 Estoque</h4>

<table class="table">
<tr>
<th>ID</th>
<th>Peça</th>
<th>Qtd</th>
</tr>

{% for p in pecas %}
<tr>
<td>{{p[0]}}</td>
<td>{{p[1]}}</td>
<td>{{p[2]}}</td>
</tr>
{% endfor %}

</table>

</div>
</div>


<div class="col-md-6">
<div class="card p-4">
<h4>🧾 Serviços</h4>

<table class="table">
<tr>
<th>ID</th>
<th>Cliente</th>
<th>Placa</th>
<th>Serviço</th>
<th>Pago</th>
</tr>

{% for s in servicos %}
<tr>
<td>{{s[0]}}</td>
<td>{{s[1]}}</td>
<td>{{s[2]}}</td>
<td>{{s[3]}}</td>
<td>
{% if s[4]=='Sim' %}
<span class="badge bg-success">Pago</span>
{% else %}
<span class="badge bg-danger">Pendente</span>
{% endif %}
</td>
</tr>
{% endfor %}

</table>

</div>
</div>

</div>

</div>

</body>
</html>
"""

# =============================
# HOME
# =============================

@app.route("/")

def home():

    conn = db()
    c = conn.cursor()

    pecas = c.execute("SELECT * FROM pecas").fetchall()
    servicos = c.execute("SELECT * FROM servicos").fetchall()

    conn.close()

    return render_template_string(layout, pecas=pecas, servicos=servicos)

# =============================
# ADD PEÇA
# =============================

@app.route("/add_peca", methods=["POST"])

def add_peca():

    nome = request.form["nome"]
    qtd = request.form["quantidade"]

    conn = db()
    c = conn.cursor()

    c.execute("INSERT INTO pecas(nome,quantidade) VALUES (?,?)", (nome, qtd))

    conn.commit()
    conn.close()

    return redirect("/")

# =============================
# ADD SERVIÇO
# =============================

@app.route("/add_servico", methods=["POST"])

def add_servico():

    cliente = request.form["cliente"]
    placa = request.form["placa"]
    descricao = request.form["descricao"]
    pago = request.form["pago"]

    conn = db()
    c = conn.cursor()

    c.execute("INSERT INTO servicos(cliente,placa,descricao,pago) VALUES (?,?,?,?)",
              (cliente, placa, descricao, pago))

    conn.commit()
    conn.close()

    return redirect("/")

# =============================
# START
# =============================

if __name__ == "__main__":
    app.run(debug=True)
