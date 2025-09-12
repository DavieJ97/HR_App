# Main page with buttons.
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from emplyee import EmployeePage
from training import TrainingPage
from additionalInfo import InfoPage


class HRApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App Page Example")
        self.setGeometry(100, 100, 400, 300)

        # Main layout
        layout = QVBoxLayout()

        # Header label
        header = QLabel("Header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # Buttons
        btn_employee = QPushButton("Employee")
        btn_training = QPushButton("Training")
        btn_info = QPushButton("Info")

        # Optional styling for buttons
        button_style = "font-size: 16px; padding: 10px;"
        btn_employee.setStyleSheet(button_style)
        btn_employee.clicked.connect(self.openEmployees)
        btn_training.setStyleSheet(button_style)
        btn_training.clicked.connect(self.openTrainings)
        btn_info.setStyleSheet(button_style)
        btn_info.clicked.connect(self.openInfo)

        # Add buttons to layout
        layout.addWidget(btn_employee)
        layout.addWidget(btn_training)
        layout.addWidget(btn_info)

        # Apply layout
        self.setLayout(layout)

    def openEmployees(self):
        self.subpageemployee = EmployeePage()
        self.subpageemployee.showMaximized()
        self.subpageemployee.show()

    def openTrainings(self):
        self.subpagetraining = TrainingPage()
        self.subpagetraining.showMaximized()
        self.subpagetraining.show()

    def openInfo(self):
        self.subpageinfo = InfoPage()
        self.subpageinfo.showMaximized()
        self.subpageinfo.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HRApp()
    window.showMaximized()
    window.show()
    sys.exit(app.exec())
