import sqlite3

# Conexão com o banco
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ==========================
# TABELA USUÁRIOS
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    telefone TEXT,
    cidade TEXT
);

""")

# ==========================
# TABELA PRODUTOS
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    categoria TEXT,
    tipo TEXT NOT NULL, -- revenda, aluguel ou troca
    preco REAL,
    imagem TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
""")

# ==========================
# TABELA PEDIDOS
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL, -- revenda, aluguel ou troca
    produto_id INTEGER NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pendente',
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);
""")

conn.commit()
conn.close()

print("Tabelas criadas com sucesso!")

# ==========================
# TABELA IMPORTADOS
# ==========================
def criar_tabela_importados():
    conn = sqlite3.connect("marketlace.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS importados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            categoria TEXT,
            tipo TEXT,
            preco REAL
        )
    """)
    conn.commit()
    conn.close()

criar_tabela_importados()
