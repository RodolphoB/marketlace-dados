import sqlite3

BANCO = "database.db"


def alterar_tabela(nome_tabela, nova_estrutura_sql, colunas_copia):
    conn = sqlite3.connect(BANCO)
    cur = conn.cursor()

    try:
        print(f"\n🔧 Ajustando tabela {nome_tabela}...")

        # 1. Criar tabela temporária com nova estrutura
        cur.execute(nova_estrutura_sql)

        # 2. Copiar apenas as colunas desejadas
        colunas = ", ".join(colunas_copia)
        cur.execute(f"""
            INSERT INTO {nome_tabela}_nova ({colunas})
            SELECT {colunas}
            FROM {nome_tabela};
        """)

        # 3. Deletar tabela antiga
        cur.execute(f"DROP TABLE {nome_tabela};")

        # 4. Renomear tabela nova
        cur.execute(f"ALTER TABLE {nome_tabela}_nova RENAME TO {nome_tabela};")

        conn.commit()
        print(f"✅ Tabela {nome_tabela} atualizada com sucesso!")

    except Exception as e:
        print(f"❌ Erro: {e}")

    conn.close()


if __name__ == "__main__":

    # EXEMPLO: remover coluna data_pedido e adicionar coluna tipo
    alterar_tabela(
        nome_tabela="pedidos",

        # NOVA estrutura da tabela
        nova_estrutura_sql="""
            CREATE TABLE pedidos_nova (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                produto_id INTEGER,
                tipo TEXT,
                status TEXT,
                data_pedido DATE,
                valor REAL
            );
        """,

        # Colunas que deseja copiar da tabela antiga
        colunas_copia=["id", "usuario_id", "produto_id", "status", "tipo", "data_pedido"]
        # OBS: Removi data_pedido e adicionei tipo
    )

