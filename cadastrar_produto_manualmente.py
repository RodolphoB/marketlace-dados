import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
INSERT INTO produtos (usuario_id, nome, descricao, categoria, tipo, preco, imagem)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (2, "Nike Air Max", "Tênis de corrida", "Esportivo", "revenda", 3500.00, "imagem.png"))

conn.commit()
conn.close()
