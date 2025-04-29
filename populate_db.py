import pandas as pd
import sqlite3

def populate_database(excel_file, db_file):
    # Connect to SQLite database (creates if not exists)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estoque_inicial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livro TEXT,
            quantidade INTEGER,
            preco REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livro TEXT,
            quantidade INTEGER,
            preco REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livro TEXT,
            comprador TEXT,
            quantidade INTEGER,
            preco REAL,
            data TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analise (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livro TEXT,
            total_vendas INTEGER,
            receita REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contatos_devedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            telefone TEXT,
            email TEXT,
            divida REAL
        )
    ''')

    conn.commit()

    # Load Excel sheets
    xls = pd.ExcelFile(excel_file)

    # Insert data into estoque_inicial
    if 'ST. INICIAL' in xls.sheet_names:
        df_estoque_inicial = pd.read_excel(xls, 'ST. INICIAL')
        df_estoque_inicial.to_sql('estoque_inicial', conn, if_exists='replace', index=False)

    # Insert data into stock
    if 'STOCK' in xls.sheet_names:
        df_stock = pd.read_excel(xls, 'STOCK')
        df_stock.to_sql('stock', conn, if_exists='replace', index=False)

    # Insert data into vendas
    if 'VENDAS' in xls.sheet_names:
        df_vendas = pd.read_excel(xls, 'VENDAS')
        df_vendas.to_sql('vendas', conn, if_exists='replace', index=False)

    # Insert data into analise
    if 'ANALISE' in xls.sheet_names:
        df_analise = pd.read_excel(xls, 'ANALISE')
        df_analise.to_sql('analise', conn, if_exists='replace', index=False)

    # Insert data into contatos_devedores
    if 'contact de devedores' in xls.sheet_names:
        df_devedores = pd.read_excel(xls, 'contact de devedores')
        df_devedores.to_sql('contatos_devedores', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Uso: python populate_db.py <arquivo_excel.xlsx> <banco_de_dados.db>")
    else:
        excel_file = sys.argv[1]
        db_file = sys.argv[2]
        populate_database(excel_file, db_file)
        print("Banco de dados populado com sucesso.")
