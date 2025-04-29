import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QMessageBox,
    QDialog, QFormLayout, QComboBox, QFileDialog
)
from PyQt5.QtCore import Qt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import csv
from fpdf import FPDF

DB_FILE = 'books.db'

class DatabaseManager:
    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def fetch_all(self, table):
        self.cursor.execute(f"SELECT * FROM {table}")
        return self.cursor.fetchall()

    def search(self, table, column, value):
        query = f"SELECT * FROM {table} WHERE {column} LIKE ?"
        self.cursor.execute(query, ('%' + value + '%',))
        return self.cursor.fetchall()

    def insert(self, table, data):
        keys = ', '.join(data.keys())
        question_marks = ', '.join(['?'] * len(data))
        values = tuple(data.values())
        query = f"INSERT INTO {table} ({keys}) VALUES ({question_marks})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def update(self, table, data, row_id):
        keys = ', '.join([f"{k}=?" for k in data.keys()])
        values = tuple(data.values()) + (row_id,)
        query = f"UPDATE {table} SET {keys} WHERE id=?"
        self.cursor.execute(query, values)
        self.conn.commit()

    def delete(self, table, row_id):
        query = f"DELETE FROM {table} WHERE id=?"
        self.cursor.execute(query, (row_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

class BookDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Livro")
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.livro_input = QLineEdit()
        self.quantidade_input = QLineEdit()
        self.preco_input = QLineEdit()

        if self.data:
            self.livro_input.setText(str(self.data.get('livro', '')))
            self.quantidade_input.setText(str(self.data.get('quantidade', '')))
            self.preco_input.setText(str(self.data.get('preco', '')))

        layout.addRow("Livro:", self.livro_input)
        layout.addRow("Quantidade:", self.quantidade_input)
        layout.addRow("Preço:", self.preco_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Salvar")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addRow(btn_layout)
        self.setLayout(layout)

    def get_data(self):
        return {
            'livro': self.livro_input.text(),
            'quantidade': int(self.quantidade_input.text()),
            'preco': float(self.preco_input.text())
        }

class VendaDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Venda")
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.livro_input = QLineEdit()
        self.comprador_input = QLineEdit()
        self.quantidade_input = QLineEdit()
        self.preco_input = QLineEdit()
        self.data_input = QLineEdit()

        if self.data:
            self.livro_input.setText(str(self.data.get('livro', '')))
            self.comprador_input.setText(str(self.data.get('comprador', '')))
            self.quantidade_input.setText(str(self.data.get('quantidade', '')))
            self.preco_input.setText(str(self.data.get('preco', '')))
            self.data_input.setText(str(self.data.get('data', '')))

        layout.addRow("Livro:", self.livro_input)
        layout.addRow("Comprador:", self.comprador_input)
        layout.addRow("Quantidade:", self.quantidade_input)
        layout.addRow("Preço:", self.preco_input)
        layout.addRow("Data (YYYY-MM-DD):", self.data_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Salvar")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addRow(btn_layout)
        self.setLayout(layout)

    def get_data(self):
        return {
            'livro': self.livro_input.text(),
            'comprador': self.comprador_input.text(),
            'quantidade': int(self.quantidade_input.text()),
            'preco': float(self.preco_input.text()),
            'data': self.data_input.text()
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestão de Livros")
        self.db = DatabaseManager()
        self.current_table = None
        self.init_ui()

    def init_ui(self):
        self.create_menu()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar por livro ou comprador")
        self.search_bar.textChanged.connect(self.search)
        self.layout.addWidget(self.search_bar)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Adicionar")
        self.add_btn.clicked.connect(self.add_entry)
        self.edit_btn = QPushButton("Editar")
        self.edit_btn.clicked.connect(self.edit_entry)
        self.delete_btn = QPushButton("Remover")
        self.delete_btn.clicked.connect(self.delete_entry)
        self.export_btn = QPushButton("Exportar Relatório")
        self.export_btn.clicked.connect(self.export_report)
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.edit_btn)
        self.btn_layout.addWidget(self.delete_btn)
        self.btn_layout.addWidget(self.export_btn)
        self.layout.addLayout(self.btn_layout)

        self.statusBar().showMessage("Pronto")
        self.show_estoque_inicial()

    def create_menu(self):
        menubar = self.menuBar()

        estoque_inicial_menu = menubar.addMenu("📚 Estoque Inicial")
        estoque_inicial_menu.triggered.connect(lambda: self.show_table('estoque_inicial'))

        estoque_atual_menu = menubar.addMenu("🏬 Estoque Atual")
        estoque_atual_menu.triggered.connect(lambda: self.show_table('stock'))

        vendas_menu = menubar.addMenu("💸 Vendas")
        vendas_menu.triggered.connect(lambda: self.show_table('vendas'))

        analise_menu = menubar.addMenu("📊 Análise de Vendas")
        analise_menu.triggered.connect(self.show_analise)

        devedores_menu = menubar.addMenu("📞 Contatos Devedores")
        devedores_menu.triggered.connect(lambda: self.show_table('contatos_devedores'))

    def show_table(self, table_name):
        self.current_table = table_name
        self.search_bar.clear()
        data = self.db.fetch_all(table_name)
        self.populate_table(data)

    def populate_table(self, data):
        if not data:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0].keys()))
        self.table.setHorizontalHeaderLabels(data[0].keys())
        for row_idx, row in enumerate(data):
            for col_idx, key in enumerate(row.keys()):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(row[key])))

    def add_entry(self):
        if self.current_table in ['estoque_inicial', 'stock', 'analise', 'contatos_devedores']:
            dialog = BookDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                self.db.insert(self.current_table, data)
                self.show_table(self.current_table)
        elif self.current_table == 'vendas':
            dialog = VendaDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                self.db.insert(self.current_table, data)
                self.show_table(self.current_table)

    def edit_entry(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma linha para editar.")
            return
        row_id = int(self.table.item(selected, 0).text())
        row_data = {}
        for col in range(self.table.columnCount()):
            header = self.table.horizontalHeaderItem(col).text()
            row_data[header] = self.table.item(selected, col).text()

        if self.current_table in ['estoque_inicial', 'stock', 'analise', 'contatos_devedores']:
            dialog = BookDialog(self, row_data)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                self.db.update(self.current_table, data, row_id)
                self.show_table(self.current_table)
        elif self.current_table == 'vendas':
            dialog = VendaDialog(self, row_data)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                self.db.update(self.current_table, data, row_id)
                self.show_table(self.current_table)

    def delete_entry(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma linha para remover.")
            return
        row_id = int(self.table.item(selected, 0).text())
        confirm = QMessageBox.question(self, "Confirmação", "Tem certeza que deseja remover este registro?")
        if confirm == QMessageBox.Yes:
            self.db.delete(self.current_table, row_id)
            self.show_table(self.current_table)

    def search(self):
        text = self.search_bar.text()
        if not text:
            self.show_table(self.current_table)
            return
        if self.current_table == 'vendas':
            results = self.db.search(self.current_table, 'livro', text)
            results += self.db.search(self.current_table, 'comprador', text)
            # Remove duplicates
            results = list({r['id']: r for r in results}.values())
        else:
            results = self.db.search(self.current_table, 'livro', text)
        self.populate_table(results)

    def show_estoque_inicial(self):
        self.show_table('estoque_inicial')

    def show_analise(self):
        self.current_table = 'analise'
        self.search_bar.clear()
        data = self.db.fetch_all('analise')
        self.populate_table(data)
        self.show_graph()

    def show_graph(self):
        data = self.db.fetch_all('analise')
        livros = [row['livro'] for row in data]
        vendas = [row['total_vendas'] for row in data]

        fig, ax = plt.subplots()
        ax.bar(livros, vendas)
        ax.set_title('Análise de Vendas por Livro')
        ax.set_xlabel('Livro')
        ax.set_ylabel('Total de Vendas')
        plt.xticks(rotation=45, ha='right')

        canvas = FigureCanvas(fig)
        graph_window = QDialog(self)
        graph_window.setWindowTitle("Gráfico de Vendas")
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        graph_window.setLayout(layout)
        graph_window.resize(600, 400)
        graph_window.exec_()

    def export_report(self):
        if not self.current_table:
            QMessageBox.warning(self, "Aviso", "Nenhuma tabela selecionada para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório", "", "CSV Files (*.csv);;PDF Files (*.pdf)")
        if not path:
            return
        data = self.db.fetch_all(self.current_table)
        if path.endswith('.csv'):
            self.export_csv(path, data)
        elif path.endswith('.pdf'):
            self.export_pdf(path, data)
        else:
            QMessageBox.warning(self, "Aviso", "Formato de arquivo não suportado.")

    def export_csv(self, path, data):
        if not data:
            QMessageBox.information(self, "Informação", "Nenhum dado para exportar.")
            return
        with open(path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data[0].keys())
            for row in data:
                writer.writerow(row)
        QMessageBox.information(self, "Sucesso", f"Relatório CSV salvo em {path}")

    def export_pdf(self, path, data):
        if not data:
            QMessageBox.information(self, "Informação", "Nenhum dado para exportar.")
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        col_width = pdf.w / (len(data[0].keys()) + 1)
        row_height = pdf.font_size * 1.5

        # Header
        for header in data[0].keys():
            pdf.cell(col_width, row_height, header, border=1)
        pdf.ln(row_height)

        # Rows
        for row in data:
            for item in row:
                pdf.cell(col_width, row_height, str(item), border=1)
            pdf.ln(row_height)

        pdf.output(path)
        QMessageBox.information(self, "Sucesso", f"Relatório PDF salvo em {path}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
