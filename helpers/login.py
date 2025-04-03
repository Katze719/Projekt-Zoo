from PySide6.QtWidgets import (
    QDialog,
    QLineEdit,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QMessageBox,
)
from helpers import db_connector


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DB Login")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Server-Eingabe
        server_layout = QHBoxLayout()
        server_label = QLabel("Server:")
        self.server_edit = QLineEdit("(localdb)\\mssqllocaldb")
        server_layout.addWidget(server_label)
        server_layout.addWidget(self.server_edit)
        layout.addLayout(server_layout)

        # Datenbank-Eingabe
        db_layout = QHBoxLayout()
        db_label = QLabel("Database:")
        self.db_edit = QLineEdit("Zoo_new")
        db_layout.addWidget(db_label)
        db_layout.addWidget(self.db_edit)
        layout.addLayout(db_layout)

        # Authentifizierungsauswahl
        auth_layout = QHBoxLayout()
        auth_label = QLabel("Authentifizierung:")
        self.auth_combo = QComboBox()
        self.auth_combo.addItems(["Windows Authentication", "SQL Server Authentication"])
        self.auth_combo.currentTextChanged.connect(self.auth_changed)
        auth_layout.addWidget(auth_label)
        auth_layout.addWidget(self.auth_combo)
        layout.addLayout(auth_layout)

        # Benutzername (nur SQL Auth)
        user_layout = QHBoxLayout()
        self.user_label = QLabel("Benutzername:")
        self.user_edit = QLineEdit()
        user_layout.addWidget(self.user_label)
        user_layout.addWidget(self.user_edit)
        layout.addLayout(user_layout)

        # Passwort (nur SQL Auth)
        pass_layout = QHBoxLayout()
        self.pass_label = QLabel("Passwort:")
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(self.pass_label)
        pass_layout.addWidget(self.pass_edit)
        layout.addLayout(pass_layout)

        # Standardmäßig deaktiviert, wenn Windows Auth gewählt
        self.auth_changed(self.auth_combo.currentText())

        # Verbindungsbutton
        self.connect_button = QPushButton("Verbinden")
        self.connect_button.clicked.connect(self.try_connect)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

    def auth_changed(self, text):
        if text == "Windows Authentication":
            self.user_edit.setDisabled(True)
            self.pass_edit.setDisabled(True)
        else:
            self.user_edit.setDisabled(False)
            self.pass_edit.setDisabled(False)

    def try_connect(self):
        driver = "ODBC Driver 17 for SQL Server"
        server = self.server_edit.text().strip()
        database = self.db_edit.text().strip()
        auth_type = self.auth_combo.currentText()
        username = self.user_edit.text().strip() if auth_type == "SQL Server Authentication" else None
        password = self.pass_edit.text() if auth_type == "SQL Server Authentication" else None

        self.db_connector = db_connector.DatabaseConnector(driver, server, database, auth_type, username, password)
        try:
            self.db_connector.connect()
        except Exception as e:
            QMessageBox.critical(self, "Verbindungsfehler", str(e))
            return
        self.accept()