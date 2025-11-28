from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import json
import requests
import datetime
from datetime import datetime
import json
import zipfile
from io import BytesIO
from flask import send_file
import requests
from flask import redirect, url_for

app = Flask(__name__)
app.secret_key = "yogurt"

DB = "database.db"

# ===========================================================
# FUNÇÃO AUXILIAR PARA CONECTAR BD
# ===========================================================
def get_db():
    return sqlite3.connect(DB)

# ===========================================================
# FUNÇÃO PARA EXPORTAR DADOS
# ===========================================================
@app.route("/exportar")
def exportar_dados():
    # 1 — Buscar dados no banco
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    cursor.execute("PRAGMA table_info(produtos)")
    columns = [col[1] for col in cursor.fetchall()]

    conn.close()

    # 2 — Transformar em lista de dicionários
    lista_produtos = [dict(zip(columns, linha)) for linha in produtos]

    dados = {
        "produtos": lista_produtos
    }

    # 3 — Criar arquivo JSON em memória
    json_bytes = json.dumps(dados, indent=4).encode("utf-8")

    # 4 — Criar ZIP em memória
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("dados.json", json_bytes)
    zip_buffer.seek(0)

    # 5 — Retornar ZIP para download
    return send_file(zip_buffer,
                     mimetype="application/zip",
                     as_attachment=True,
                     download_name="dados_marketlace.zip")

# ===========================================================
# FUNÇÃO PARA IMPORTAR DADOS
# ===========================================================
@app.route("/importar")
def importar_dados():
    url = "https://raw.githubusercontent.com/SEU_REPOSITORIO/dados.json"

    try:
        resposta = requests.get(url)
        dados = resposta.json()

        produtos = dados.get("produtos", [])

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        for p in produtos:
            cursor.execute("""
                INSERT INTO importados (nome, categoria, tipo, preco)
                VALUES (?, ?, ?, ?)
            """, (p["nome"], p["categoria"], p["tipo"], p["preco"]))

        conn.commit()
        conn.close()

        return redirect(url_for("dados_importados"))

    except Exception as e:
        return f"Erro ao importar dados: {e}"
    
@app.route("/importados")
def dados_importados():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT nome, categoria, tipo, preco FROM importados")
    itens = cursor.fetchall()

    conn.close()

    return render_template("importados.html", itens=itens)

# ===========================================================
# HOME
# ===========================================================
@app.route("/")
def home():
    return render_template("home.html")


# ===========================================================
# FUNCIONALIDADES PRINCIPAIS (PÚBLICAS)
# ===========================================================
@app.route("/alugar")
def alugar():
    return render_template("aluguel.html")

@app.route("/trocar")
def trocar():
    return render_template("trocas.html")

@app.route("/revender")
def revender():
    return render_template("revenda.html")


# ===========================================================
# AUTENTICAÇÃO
# ===========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email 
            FROM usuarios 
            WHERE email = ? AND senha = ?
        """, (email, senha))

        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session["user_id"] = usuario[0]
            session["user_nome"] = usuario[1]
            return redirect("/minha-conta")
        else:
            return render_template("login.html", erro="Email ou senha incorretos")

    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar = request.form.get("confirmar")

        # Verificar senha
        if senha != confirmar:
            return "As senhas não coincidem!"

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha)
            VALUES (?, ?, ?)
        """, (nome, email, senha))

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("cadastro.html")



# ===========================================================
# ÁREA DO USUÁRIO
# ===========================================================
@app.route("/minha-conta")
def minha_conta():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("minha_conta.html")


@app.route("/perfil")
def perfil():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome, email, telefone, cidade 
        FROM usuarios 
        WHERE id = ?
    """, (session["user_id"],))

    user = cursor.fetchone()
    conn.close()

    return render_template("perfil.html", user=user)


@app.route('/editar-perfil', methods=['GET', 'POST'])
def editar_perfil():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        cidade = request.form['cidade']

        cursor.execute("""
            UPDATE usuarios 
            SET nome=?, email=?, telefone=?, cidade=?
            WHERE id=?
        """, (nome, email, telefone, cidade, user_id))

        conn.commit()
        conn.close()
        return redirect(url_for('perfil'))

    cursor.execute("SELECT nome, email, telefone, cidade FROM usuarios WHERE id=?", (user_id,))
    usuarios = cursor.fetchone()

    conn.close()

    return render_template('editar_perfil.html', usuarios=usuarios)


@app.route("/carteira")
def carteira():
    return render_template("carteira.html")

@app.route("/configuracoes")
def configuracoes():
    return render_template("configuracoes.html")


# ===========================================================
# MINHAS AÇÕES
# ===========================================================
@app.route("/meus-anuncios")
def meus_anuncios():
    if "user_id" not in session:
        return redirect(url_for("login"))

    usuario_id = session["user_id"]
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, descricao, categoria, tipo, preco, imagem
        FROM produtos
        WHERE usuario_id = ?
        ORDER BY data_criacao DESC
    """, (usuario_id,))

    produtos = cur.fetchall()
    conn.close()
    return render_template("meus_anuncios.html", produtos=produtos)

@app.route("/seguranca", methods=["GET", "POST"])
def seguranca():
    # só permite usuário logado
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # POST -> confirmar exclusão
    if request.method == "POST":
        confirmar = request.form.get("confirmar")
        if confirmar != "SIM":
            # se o usuário não confirmou com "SIM", volta para a mesma página com mensagem
            return render_template("seguranca.html", erro="Você precisa digitar 'SIM' para confirmar a exclusão da conta.")

        conn = get_db()
        cursor = conn.cursor()

        # -- remover dados relacionados (se existirem tabelas relacionadas)
        # tenta apagar registros conectados em produtos e pedidos caso existam
        try:
            cursor.execute("DELETE FROM produtos WHERE usuario_id = ?", (user_id,))
        except Exception:
            pass

        try:
            cursor.execute("DELETE FROM pedidos WHERE usuario_id = ?", (user_id,))
        except Exception:
            pass

        # apagar usuário
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))

        conn.commit()
        conn.close()

        # limpar session e redirecionar para home com mensagem
        session.pop("user_id", None)
        session.pop("user_nome", None)
        return redirect(url_for("home"))

    # GET -> mostrar página de segurança (form de exclusão)
    return render_template("seguranca.html")


@app.route("/enderecos")
def enderecos():
    return "<h1>Endereços (em construção)</h1>"


@app.route("/verificacao")
def verificacao():
    return "<h1>Verificação (em construção)</h1>"


@app.route("/notificacoes")
def notificacoes():
    return "<h1>Notificações (em construção)</h1>"

@app.route("/meus-produtos")
def meus_produtos():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE usuario_id = ?", (session["user_id"],))
    produtos = cursor.fetchall()
    conn.close()

    return render_template("produtos/meus_produtos.html", produtos=produtos)

@app.route("/produto/novo")
def produto_novo():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("produtos/novo.html")

@app.route("/produto/editar/<int:id>")
def produto_editar(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ? AND usuario_id = ?", (id, session["user_id"]))
    produto = cursor.fetchone()
    conn.close()

    return render_template("produtos/editar.html", produto=produto)

@app.route("/produto/editar/<int:id>", methods=["POST"])
def produto_editar_post(id):
    nome = request.form["nome"]
    descricao = request.form["descricao"]
    categoria = request.form["categoria"]
    tipo = request.form["tipo"]
    preco = request.form["preco"]
    imagem = request.form["imagem"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE produtos SET nome=?, descricao=?, categoria=?, tipo=?, preco=?, imagem=?
        WHERE id=? AND usuario_id=?
    """, (nome, descricao, categoria, tipo, preco, imagem, id, session["user_id"]))

    conn.commit()
    conn.close()

    return redirect("/meus-produtos")

@app.route("/produto/deletar/<int:id>", methods=["POST"])
def produto_deletar(id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id=? AND usuario_id=?", (id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect("/meus-produtos")
# ===========================================================
# PEDIDOS
# ===========================================================
@app.route('/novo_pedido', methods=['POST'])
def novo_pedido():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    usuario_id = session['user_id']
    produto_id = request.form['produto_id']
    tipo = request.form['tipo']
    
    data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO pedidos (usuario_id, produto_id, tipo, status, data_pedido)
        VALUES (?, ?, ?, ?, ?)
    """, (usuario_id, produto_id, tipo, "pendente", data))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('meus_pedidos'))

@app.route('/meus_pedidos')
def meus_pedidos():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    usuario_id = session['user_id']

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT p.id, pr.nome, pr.imagem, pr.tipo, p.status, p.data_pedido
        FROM pedidos p
        JOIN produtos pr ON pr.id = p.produto_id
        WHERE p.usuario_id = ?
        ORDER BY p.data_pedido DESC
    """, (usuario_id,))

    pedidos = cur.fetchall()
    conn.close()

    return render_template('meus_pedidos.html', pedidos=pedidos)

@app.route("/pedidos/editar/<int:id>", methods=["GET"])
def editar_pedido(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, produto_id, tipo, status, valor
        FROM pedidos
        WHERE id = ? AND usuario_id = ?
    """, (id, session["user_id"]))

    pedido = cursor.fetchone()
    conn.close()

    if not pedido:
        return "Pedido não encontrado", 404

    return render_template("editar_pedido.html", pedido=pedido)

@app.route("/pedidos/editar/<int:id>", methods=["POST"])
def atualizar_pedido(id):
    if "user_id" not in session:
        return redirect("/login")

    tipo = request.form["tipo"]
    status = request.form["status"]
    valor = request.form["valor"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE pedidos
        SET tipo = ?, status = ?, valor = ?
        WHERE id = ? AND usuario_id = ?
    """, (tipo, status, valor, id, session["user_id"]))

    conn.commit()
    conn.close()

    return redirect("/meus_pedidos")

# ===========================================================
# PRODUTOS
# ===========================================================
@app.route('/editar-produto/<int:produto_id>', methods=['GET', 'POST'])
def editar_produto(produto_id):
    # Aqui você pode buscar o produto pelo ID e renderizar o formulário de edição
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    produto = cur.fetchone()
    conn.close()

    if not produto:
        return "Produto não encontrado", 404

    if request.method == 'POST':
        # Aqui você processaria o formulário de edição
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']
        cur = sqlite3.connect('database.db').cursor()
        cur.execute("UPDATE produtos SET nome=?, descricao=?, preco=? WHERE id=?", 
                    (nome, descricao, preco, produto_id))
        cur.connection.commit()
        return redirect(url_for('meus_anuncios'))

    return render_template('editar_produto.html', produto=produto)

@app.route('/remover-produto/<int:produto_id>', methods=['POST'])
def remover_produto(produto_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('meus_anuncios'))

@app.route("/criar-anuncio", methods=["GET"])
def criar_anuncio():
    return render_template("criar_anuncio.html")

@app.route("/produto/novo", methods=["POST"])
def novo_produto():
    if 'user_id' not in session:
        return redirect(url_for("login"))

    usuario_id = session['user_id']
    nome = request.form['nome']
    descricao = request.form['descricao']
    categoria = request.form['categoria']
    tipo = request.form['tipo']
    preco = request.form['preco']
    imagem = request.form['imagem']

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO produtos (usuario_id, nome, descricao, categoria, tipo, preco, imagem)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (usuario_id, nome, descricao, categoria, tipo, preco, imagem))
    conn.commit()
    conn.close()

    return redirect(url_for("meus_anuncios"))
# ===========================================================
# FEED E DETALHES
# ===========================================================
@app.route("/feed")
def feed():
    return render_template("feed.html")

@app.route("/detalhes/<int:produto_id>")
def detalhes(produto_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, usuario_id, nome, descricao, categoria, tipo, preco, imagem, data_criacao
        FROM produtos
        WHERE id = ?
    """, (produto_id,))

    produto = cur.fetchone()
    conn.close()

    if not produto:
        return "Produto não encontrado", 404

    # Convertendo para dicionário
    produto_dict = {
        "id": produto[0],
        "usuario_id": produto[1],
        "nome": produto[2],
        "descricao": produto[3],
        "categoria": produto[4],
        "tipo": produto[5],
        "preco": produto[6],
        "imagem": produto[7],
        "data_criacao": produto[8]
    }

    return render_template("detalhes.html", produto=produto_dict)




# ===========================================================
# RUN
# ===========================================================
if __name__ == "__main__":
    app.run(debug=True)
