import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QLineEdit, QFormLayout, QMessageBox, QDialog, QDialogButtonBox, QListWidget, QInputDialog
)
from PyQt6.QtCore import Qt


# Password dialog
class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        print('making dialog')
        self.setWindowTitle("Enter Password")

        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.EchoMode.Password)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Please enter password:"))
        layout.addWidget(self.input)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def getPassword(self):
        return self.input.text()

class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Password")

        self.newPass1 = QLineEdit()
        self.newPass1.setEchoMode(QLineEdit.EchoMode.Password)

        self.newPass2 = QLineEdit()
        self.newPass2.setEchoMode(QLineEdit.EchoMode.Password)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter New Password:"))
        layout.addWidget(self.newPass1)
        layout.addWidget(QLabel("Confirm New Password:"))
        layout.addWidget(self.newPass2)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def getPasswords(self):
        return self.newPass1.text(), self.newPass2.text()


class InfoPage(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect("hr_app.db")
        self.cursor = self.conn.cursor()
        self.password = "admin123"  # fallback in case no password in DB
        self.load_password_from_db()
        self.initUI()

    def load_password_from_db(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
        self.conn.commit()
        self.cursor.execute("SELECT value FROM settings WHERE key='password'")
        row = self.cursor.fetchone()
        if row:
            self.password = row[0]
        else:
            self.cursor.execute("INSERT INTO settings (key, value) VALUES ('password', ?)", (self.password,))
            self.conn.commit()

    def initUI(self):
        layout = QVBoxLayout()

        # Header
        header = QLabel("Header")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header)

        # Scrollable Info Section
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.form_layout = QFormLayout(scroll_content)

        # Company info fields
        self.company_name = QLineEdit()
        self.company_type = QLineEdit()
        self.departments = QLineEdit()

        # Load info from DB
        self.load_info()

        # Start in read-only mode
        self.set_fields_editable(False)
        self.departments.setReadOnly(True)

        # Add fields to form layout
        self.form_layout.addRow("Company Name:", self.company_name)
        self.form_layout.addRow("Company Type:", self.company_type)
        self.form_layout.addRow("Departments:", self.departments)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Buttons
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.enable_editing)
        layout.addWidget(self.edit_button)

        self.extra_button = QPushButton("Change Password")
        self.extra_button.clicked.connect(self.change_password)
        layout.addWidget(self.extra_button)

        self.setLayout(layout)

    def set_fields_editable(self, editable):
        self.company_name.setReadOnly(not editable)
        self.company_type.setReadOnly(not editable)

    def load_info(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_info (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT
            )
        """)
        self.conn.commit()

        self.cursor.execute("SELECT name, type FROM company_info WHERE id=1")
        row = self.cursor.fetchone()
        departments = self.load_dept_info()
        if row:
            self.company_name.setText(row[0])
            self.company_type.setText(row[1])
            self.departments.setText(departments)
        else:
            self.cursor.execute(
                "INSERT INTO company_info (id, name, type) VALUES (1, '', '')"
            )
            self.conn.commit()

    def load_dept_info(self):
        self.cursor.execute("SELECT name FROM departments ORDER BY name")
        rows = self.cursor.fetchall()
        # Extract names and join with commas
        dept_list = [row[0] for row in rows]
        return ", ".join(dept_list)

    def enable_editing(self):
        dialog = PasswordDialog(self)
        if dialog.exec():
            entered = dialog.getPassword()
            if entered == self.password:
                self.set_fields_editable(True)
                self.edit_button.setText("Save")
                self.edit_button.clicked.disconnect()
                self.edit_button.clicked.connect(self.save_info)
                self.extra_button.setVisible(True)
                self.extra_button.setText("Add New Department")
                self.extra_button.clicked.disconnect()
                self.extra_button.clicked.connect(self.add_department)
            else:
                QMessageBox.warning(self, "Error", "Incorrect password")

    def save_info(self):
        name = self.company_name.text()
        ctype = self.company_type.text()

        self.cursor.execute("""
            UPDATE company_info SET name=?, type=? WHERE id=1
        """, (name, ctype))
        self.conn.commit()

        self.set_fields_editable(False)
        self.edit_button.setText("Edit")
        self.edit_button.clicked.disconnect()
        self.edit_button.clicked.connect(self.enable_editing)
        QMessageBox.information(self, "Saved", "Company info updated")
        self.extra_button.setText("Change Password")
        self.extra_button.clicked.connect(self.change_password)


    def change_password(self):
        dialog = ChangePasswordDialog(self)
        if dialog.exec():
            new_pass1, new_pass2 = dialog.getPasswords()
            if new_pass1 and new_pass2 and new_pass1 == new_pass2:
                self.password = new_pass1
                self.cursor.execute("UPDATE settings SET value=? WHERE key='password'", (new_pass1,))
                self.conn.commit()
                QMessageBox.information(self, "Success", "Password updated.")
            else:
                QMessageBox.warning(self, "Error", "Passwords do not match.")
            

    def add_department(self):
        new_dept, ok = QInputDialog.getText(self, "Add Department", "Department name:")
        if ok and new_dept:
            new_dept = new_dept.strip()
            if not new_dept:
                QMessageBox.warning(self, "Error", "Department name cannot be empty.")
                return

            try:
                # Insert into departments table
                self.cursor.execute("INSERT INTO departments (name) VALUES (?)", (new_dept,))
                self.conn.commit()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", f"Department '{new_dept}' already exists.")
                return

            # Update the line edit with the new list of departments
            self.departments.setText(self.load_dept_info())
            QMessageBox.information(self, "Success", f"Department '{new_dept}' added.")