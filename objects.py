# objects for app
from PyQt6.QtWidgets import QPushButton, QCheckBox, QLabel, QComboBox, QScrollArea, QLineEdit, QListWidget
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtCore import Qt, QSize

class Button(QPushButton):
    def __init___(self, width, height, img_path = None, text = None):
        super().__init__()
        self.setFixedSize(width, height)
        if img_path is not None:
            self.setIcon(QIcon(img_path))
            self.setIconSize(QSize(width-30, height-30))
        if text is not None:
            if height >= 100:
                font_size = 30
            elif height >= 80:
                font_size = 24
            elif height >= 60:
                font_size = 18
            elif height >= 40:
                font_size = 14
            else:
                font_size = 10
            self.font = QFont("Segoe UI", font_size, 700)
            self.setText(text)
            self.setFont(self.font) 

        self.setStyleSheet("""
                QPushButton {
                    border-radius: 25px;  /* Round edges */
                    border: 2px solid #b3ebde; /* Blue border */
                    background-color: #b3ebde; /* Light blue background */
                    color: black; /* White text */
                }
                QPushButton:hover {
                    background-color: #3399FF; /* Darker blue on hover */
                }
                QPushButton:pressed {
                    background-color: #0056b3; /* Even darker on click */
                }
            """)

class ToggleSwitch(QCheckBox):
    def __init__(self, text = None):
        super().__init__()
        self.setTristate(False)
        self.setStyleSheet("""
            QCheckBox::indicator {
                width: 40px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                border-radius: 10px;
                background-color: lightgrey;
            }
            QCheckBox::indicator:checked {
                border-radius: 10px;
                background-color: #4CAF50;
            }
        """)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        if text is not None:
            self.setText(text)
            font = QFont("Segoe UI", 14, 400) 
            self.setFont(font)     

class Label(QLabel):
    def __init__(self, text = None, font_size = None):
        super().__init__()
        if text is not None and font_size is not None:
            font = QFont("Segoe UI", font_size, 700)
            self.setText(text)
            self.setFont(font)

class ScrollArea(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #cbe7e2;
                width: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #3399FF;
                min-height: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #0056b3;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                subcontrol-origin: margin;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }

            QScrollBar:horizontal {
                border: none;
                background: #cbe7e2;
                height: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal {
                background: #3399FF;
                min-width: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #0056b3;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
                subcontrol-origin: margin;
            }

            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
            """)
        
class LineEdit(QLineEdit):
    def __init__(self, size = None):
        super().__init__()
        if size is not None:
            self.setFixedWidth(size)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #b0b0b0;
                border-radius: 10px;
                padding: 5px 10px;
                background-color: #dcdcdc;
                color: black;
                selection-background-color: #a0a0a0;
            }
        """)
        font = QFont("Segoe UI", 14, 400) 
        self.setFont(font)

class ListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QListWidget {
                border: 2px solid #b0b0b0;
                border-radius: 10px;
                background-color: #dcdcdc;
                color: black;
                padding: 5px;
            }

            QListWidget::item {
                padding: 5px 10px;
                border-radius: 5px;
            }

            QListWidget::item:selected {
                background-color: #a0a0a0;
                color: white;
            }
        """)
        font = QFont("Segoe UI", 14, 400) 
        self.setFont(font)


