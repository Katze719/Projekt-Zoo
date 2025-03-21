import sys
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QListWidget, QTextEdit, QTableWidget, QTableWidgetItem, QApplication,
)
from PySide6.QtGui import QIcon
from helpers import login, addEmployee

from qt_material import apply_stylesheet


# Änderungen im MainWindow (nur der relevante Code)
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db_connector):
        super().__init__()
        self.setWindowTitle("DB Abfragen App")
        self.setWindowIcon(QIcon("eggplant.png"))
        self.db_connector = db_connector
        self.setup_ui()
        self.load_views()
        self.load_user_roles()

    def setup_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # Header als eigenes Widget mit fester Höhe
        header_widget = QtWidgets.QWidget()
        header_widget.setFixedHeight(40)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.addStretch()

        self.role_label = QLabel("Rolle(n): Unbekannt")
        header_layout.addWidget(self.role_label)

        # Button "Mitarbeiter hinzufügen" – standardmäßig verborgen
        self.add_employee_button = QPushButton("Mitarbeiter hinzufügen")
        self.add_employee_button.setVisible(False)
        self.add_employee_button.clicked.connect(self.open_add_employee_dialog)
        header_layout.addWidget(self.add_employee_button)

        main_layout.addWidget(header_widget)

        # Horizontaler Splitter: Links Views-Liste, rechts Abfrage- und Ergebnisbereich
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        self.views_list = QListWidget()
        self.views_list.itemClicked.connect(self.view_selected)
        splitter.addWidget(self.views_list)

        # Rechter Bereich: Vertikaler Splitter zwischen Abfrageeingabe und Ergebnistabelle
        right_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        query_panel = QtWidgets.QWidget()
        query_layout = QtWidgets.QVBoxLayout(query_panel)
        self.info_label = QLabel("Geben Sie Ihre SQL-Abfrage ein:")
        query_layout.addWidget(self.info_label)
        self.query_text = QTextEdit()
        query_layout.addWidget(self.query_text)
        self.execute_button = QPushButton("Abfrage ausführen")
        self.execute_button.clicked.connect(self.run_query)
        query_layout.addWidget(self.execute_button)
        query_panel.setLayout(query_layout)
        right_splitter.addWidget(query_panel)

        result_panel = QtWidgets.QWidget()
        result_layout = QtWidgets.QVBoxLayout(result_panel)
        self.result_table = QTableWidget()
        result_layout.addWidget(self.result_table)
        result_panel.setLayout(result_layout)
        right_splitter.addWidget(result_panel)
        right_splitter.setSizes([150, 350])
        splitter.addWidget(right_splitter)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

    def open_add_employee_dialog(self):
        dialog = addEmployee.AddEmployeeDialog(self.db_connector, self)
        dialog.exec()

    def view_selected(self, item):
        view_name = item.text()
        # Automatische Ausführung der View: SELECT * FROM <View>
        query = f"SELECT * FROM {view_name};"
        self.query_text.setText(query)
        self.run_query()

    def run_query(self):
        query = self.query_text.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie eine SQL-Abfrage ein.")
            return
        try:
            columns, results = self.db_connector.execute_query(query)
            if columns and results is not None:
                self.populate_table(columns, results)
            else:
                QMessageBox.information(self, "Erfolg", "Abfrage erfolgreich ausgeführt. Keine Ergebnisse zum Anzeigen.")
                self.result_table.clear()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

    def populate_table(self, columns, data):
        self.result_table.clear()
        self.result_table.setColumnCount(len(columns))
        self.result_table.setRowCount(len(data))
        self.result_table.setHorizontalHeaderLabels(columns)
        for row_idx, row in enumerate(data):
            for col_idx, cell in enumerate(row):
                self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell)))
        self.result_table.resizeColumnsToContents()

    def load_views(self):
        query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS;"
        try:
            columns, results = self.db_connector.execute_query(query)
            if columns and results is not None:
                self.views_list.clear()
                for row in results:
                    self.views_list.addItem(row[0])
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Views: {e}")

    def load_user_roles(self):
        query = """
        SELECT dp.name AS DatabaseRole
        FROM sys.database_role_members drm
        JOIN sys.database_principals dp ON drm.role_principal_id = dp.principal_id
        JOIN sys.database_principals up ON drm.member_principal_id = up.principal_id
        WHERE up.name = USER_NAME();
        """
        try:
            columns, results = self.db_connector.execute_query(query)
            if results and len(results) > 0:
                roles = [row[0] for row in results]
                self.role_label.setText("Rolle(n): " + ", ".join(roles))
                if "VERWALTUNG" in roles:
                    self.add_employee_button.setVisible(True)
            else:
                self.role_label.setText("Rolle(n): Keine")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Rollen: {e}")

def main():
    app = QApplication(sys.argv)
    login_dialog = login.LoginDialog()
    apply_stylesheet(login_dialog, 'light_blue.xml', invert_secondary=True)
    if login_dialog.exec() == QDialog.Accepted:
        db_connector = login_dialog.db_connector
        main_window = MainWindow(db_connector)
        apply_stylesheet(main_window, 'light_blue.xml', invert_secondary=True)
        main_window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
