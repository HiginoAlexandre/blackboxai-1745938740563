# Sistema de Gestão de Livros

Este sistema em Python com interface gráfica PyQt5 permite gerenciar livros com base em dados importados de um arquivo Excel. Ele utiliza um banco de dados SQLite para armazenar as informações.

## Funcionalidades

- Importação de dados de cinco planilhas Excel: Estoque Inicial, Stock, Vendas, Análise, Contatos Devedores.
- Menus para navegar entre as seções:
  - Estoque Inicial
  - Estoque Atual
  - Vendas
  - Análise de Vendas
  - Contatos Devedores
- Adicionar, editar e remover livros e vendas.
- Atualização automática dos totais de estoque e análise.
- Exibição de gráficos de desempenho de vendas.
- Busca por nome de livro ou comprador.
- Exportação de relatórios em PDF ou CSV.

## Requisitos

- Python 3.x
- Bibliotecas Python:
  - PyQt5
  - pandas
  - matplotlib
  - fpdf

Instale as dependências com:

```
pip install PyQt5 pandas matplotlib fpdf
```

## Uso

1. Popule o banco de dados SQLite a partir do arquivo Excel:

```
python populate_db.py arquivo_dados.xlsx books.db
```

2. Execute o sistema:

```
python app.py
```

## Estrutura dos arquivos

- `populate_db.py`: Script para importar dados do Excel para o banco SQLite.
- `app.py`: Aplicação principal com interface gráfica.
- `books.db`: Banco de dados SQLite gerado após a importação.
- `README.md`: Manual básico de uso.

## Observações

- O arquivo Excel deve conter as planilhas: `ST. INICIAL`, `STOCK`, `VENDAS`, `ANALISE`, `contact de devedores`.
- Os relatórios podem ser exportados em CSV ou PDF a partir da interface do sistema.

---
Sistema desenvolvido para gerenciar livros e vendas de forma simples e eficiente.
