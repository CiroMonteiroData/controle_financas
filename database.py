"""
Módulo de acesso ao banco de dados SQLite para o app de controle financeiro.
"""
import sqlite3
import pandas as pd
from datetime import date

DB_PATH = "financas.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK (tipo IN ('Receita', 'Despesa')),
            UNIQUE(nome, tipo)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK (tipo IN ('Receita', 'Despesa')),
            categoria TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            mes TEXT NOT NULL,
            limite REAL NOT NULL,
            UNIQUE(categoria, mes)
        )
    """)

    conn.commit()

    # Categorias padrão, inseridas apenas se a tabela estiver vazia
    cur.execute("SELECT COUNT(*) FROM categorias")
    if cur.fetchone()[0] == 0:
        padrao = [
            ("Salário", "Receita"), ("Freelance", "Receita"), ("Investimentos", "Receita"),
            ("Outras Receitas", "Receita"),
            ("Alimentação", "Despesa"), ("Moradia", "Despesa"), ("Transporte", "Despesa"),
            ("Saúde", "Despesa"), ("Educação", "Despesa"), ("Lazer", "Despesa"),
            ("Compras", "Despesa"), ("Contas", "Despesa"), ("Outras Despesas", "Despesa"),
        ]
        cur.executemany("INSERT INTO categorias (nome, tipo) VALUES (?, ?)", padrao)
        conn.commit()

    conn.close()


# ---------------------- CATEGORIAS ----------------------

def listar_categorias(tipo=None):
    conn = get_connection()
    if tipo:
        df = pd.read_sql_query(
            "SELECT * FROM categorias WHERE tipo = ? ORDER BY nome", conn, params=(tipo,)
        )
    else:
        df = pd.read_sql_query("SELECT * FROM categorias ORDER BY tipo, nome", conn)
    conn.close()
    return df


def adicionar_categoria(nome, tipo):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO categorias (nome, tipo) VALUES (?, ?)", (nome, tipo))
        conn.commit()
        return True, "Categoria adicionada com sucesso."
    except sqlite3.IntegrityError:
        return False, "Essa categoria já existe para esse tipo."
    finally:
        conn.close()


def remover_categoria(categoria_id):
    conn = get_connection()
    conn.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
    conn.commit()
    conn.close()


# ---------------------- TRANSAÇÕES ----------------------

def adicionar_transacao(data_str, tipo, categoria, descricao, valor):
    conn = get_connection()
    conn.execute(
        "INSERT INTO transacoes (data, tipo, categoria, descricao, valor) VALUES (?, ?, ?, ?, ?)",
        (data_str, tipo, categoria, descricao, valor),
    )
    conn.commit()
    conn.close()


def listar_transacoes():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM transacoes ORDER BY data DESC, id DESC", conn)
    conn.close()
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
    return df


def atualizar_transacao(id_, data_str, tipo, categoria, descricao, valor):
    conn = get_connection()
    conn.execute(
        "UPDATE transacoes SET data=?, tipo=?, categoria=?, descricao=?, valor=? WHERE id=?",
        (data_str, tipo, categoria, descricao, valor, id_),
    )
    conn.commit()
    conn.close()


def remover_transacao(id_):
    conn = get_connection()
    conn.execute("DELETE FROM transacoes WHERE id = ?", (id_,))
    conn.commit()
    conn.close()


# ---------------------- ORÇAMENTOS ----------------------

def definir_orcamento(categoria, mes, limite):
    conn = get_connection()
    conn.execute(
        """INSERT INTO orcamentos (categoria, mes, limite) VALUES (?, ?, ?)
           ON CONFLICT(categoria, mes) DO UPDATE SET limite=excluded.limite""",
        (categoria, mes, limite),
    )
    conn.commit()
    conn.close()


def listar_orcamentos(mes=None):
    conn = get_connection()
    if mes:
        df = pd.read_sql_query(
            "SELECT * FROM orcamentos WHERE mes = ? ORDER BY categoria", conn, params=(mes,)
        )
    else:
        df = pd.read_sql_query("SELECT * FROM orcamentos ORDER BY mes DESC, categoria", conn)
    conn.close()
    return df


def remover_orcamento(id_):
    conn = get_connection()
    conn.execute("DELETE FROM orcamentos WHERE id = ?", (id_,))
    conn.commit()
    conn.close()
