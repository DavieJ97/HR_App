# Main page with buttons.
import sys
import sqlite3
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFrame, QHBoxLayout, QMessageBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
from employee import EmployeePage
from training import TrainingPage
from additionalInfo import InfoPage
import objects

def resource_path(relative_path):
    """Get absolute path to resource, works for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class HRApp(QWidget):  
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HR Training App")
        self.setGeometry(100, 100, 300, 300)  # Bigger, dashboard feel

        self.conn = sqlite3.connect(resource_path("hr_app.db"))
        self.cursor = self.conn.cursor()
        self.init_db()  # create tables here


        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {objects.COLOR_DARK_GREEN}, stop:0.5 {objects.COLOR_TEAL}, stop:1 {objects.COLOR_MINT}
                );
                font-family: Segoe UI, Arial, sans-serif;
            }}
        """)

        # Main layout
        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Header label
        header = objects.HeaderLabel("Taining Aid App(Demo)")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer_layout.addWidget(header)

        card = objects.Card()
        card_layout = QVBoxLayout()
        card_layout.setSpacing(10)

        # Buttons
        btn_employee = objects.StyledButton("Employee")
        btn_employee.setIcon(QIcon(resource_path("icons/employee.png")))   # 👤 user icon
        btn_employee.setIconSize(QSize(32, 32))
                                 
        btn_training = objects.StyledButton("Training")
        btn_training.setIcon(QIcon(resource_path("icons/training.png")))   # 🎓 training cap
        btn_training.setIconSize(QSize(32, 32))

        btn_info = objects.StyledButton("Info")
        btn_info.setIcon(QIcon(resource_path("icons/info.png")))           # ℹ️ info circle
        btn_info.setIconSize(QSize(32, 32))

        # Optional styling for buttons
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 18px;
                padding: 12px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        # btn_employee.setStyleSheet(button_style)
        btn_employee.clicked.connect(self.openEmployees)
        # btn_training.setStyleSheet(button_style)
        btn_training.clicked.connect(self.openTrainings)
        # btn_info.setStyleSheet(button_style)
        btn_info.clicked.connect(self.openInfo)

        # for btn in (btn_employee, btn_training, btn_info):
        #     btn.setStyleSheet(button_style)

        # Add to card
        card_layout.addWidget(btn_employee)
        card_layout.addWidget(btn_training)
        card_layout.addWidget(btn_info)
        card.setLayout(card_layout)

         # === CENTER ALIGN CARD ===
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        center_layout.addStretch()

        outer_layout.addLayout(center_layout)

        # Apply layout
        self.setLayout(outer_layout)

    def init_db(self):
        """Create all required tables if they don't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_info (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id TEXT,
                name TEXT,
                job TEXT,
                department TEXT
            )
        """)
        self.conn.commit()

    def openEmployees(self):
        try:
            self.subpageemployee = EmployeePage()
            self.subpageemployee.showMaximized()
            self.subpageemployee.show()
        except Exception as e:
            QMessageBox.critical(self, "Loading", f"Failed to load employees:\n{e}")

    def openTrainings(self):
        try:
            self.subpagetraining = TrainingPage()
            self.subpagetraining.showMaximized()
            self.subpagetraining.show()
        except Exception as e:
            QMessageBox.critical(self, "Loading", f"Failed to load trainings:\n{e}")

    def openInfo(self):
        try:
            self.subpageinfo = InfoPage()
            self.subpageinfo.showMaximized()
            self.subpageinfo.show()
        except Exception as e:
            QMessageBox.critical(self, "Loading", f"Failed to load info:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HRApp()
    window.show()
    sys.exit(app.exec())
