# objects.py

from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QPushButton, QLabel, QGraphicsDropShadowEffect, QFrame, QTableWidget, QDialog, QVBoxLayout

# 🎨 Colour palette (from your scheme)
COLOR_PRIMARY_DARK = "#031716"  # Almost black, good for text or headers
COLOR_DARK_GREEN   = "#032F30"
COLOR_TEAL         = "#0A7075"
COLOR_MINT         = "#0C969C"
COLOR_LIGHT_BLUE   = "#6BA3BE"
COLOR_SLATE        = "#274D60"

# 🎨 Assigning roles
BACKGROUND_COLOR   = COLOR_DARK_GREEN
PRIMARY_COLOR      = COLOR_TEAL
SECONDARY_COLOR    = COLOR_MINT
ACCENT_COLOR       = COLOR_LIGHT_BLUE
TEXT_COLOR         = "#FFFFFF"  # White text for contrast

# 📝 Fonts
HEADER_FONT = QFont("Arial", 14, QFont.Weight.Bold)
BODY_FONT   = QFont("Arial", 11)
SMALL_FONT  = QFont("Arial", 9)

def apply_card_shadow(widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)   # softness
        shadow.setXOffset(0)       # horizontal offset
        shadow.setYOffset(5)       # vertical offset
        shadow.setColor(QColor(0, 0, 0, 150))  # RGBA (black with transparency)
        widget.setGraphicsEffect(shadow)

# 🔘 Styled reusable button
class StyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(BODY_FONT)
        self.setStyleSheet(f"""
           QPushButton {{
                background-color: {COLOR_TEAL};
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 10px;
                text-align: left;
                qproperty-iconSize: 28px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_MINT};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_SLATE};
            }}
        """)

# 🔖 Styled reusable label
class HeaderLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(HEADER_FONT)
        self.setStyleSheet(f"""
            color: {COLOR_LIGHT_BLUE};
            font-size: 28px;
            font-weight: bold;
            padding: 20px;
        """)

class Card(QFrame):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid {COLOR_SLATE};
                border-radius: 15px;
                padding: 30px;
            }}
        """)
        apply_card_shadow(self)



class Table(QTableWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLOR_PRIMARY_DARK};
                alternate-background-color: {COLOR_DARK_GREEN};
                gridline-color: {COLOR_TEAL};
                color: white;
                border: none;
                font-size: 14px;
                selection-background-color: {COLOR_MINT};
                selection-color: white;
            }}
            QHeaderView::section {{
                background-color: {COLOR_SLATE};
                color: white;
                font-weight: bold;
                border: none;
                padding: 6px;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
        """)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)

class FloatingButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(60, 60)
        self.setStyleSheet(f"""
            QPushButton {{
                border-radius: 30px;
                background-color: {COLOR_TEAL};
                color: white;
                font-size: 26px;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_MINT};
            }}
        """)

        apply_card_shadow(self)

class ButtonFrame(QFrame):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_DARK_GREEN};
                border-radius: 8px;
                padding: 8px;
            }}
        """)

class TableStyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(BODY_FONT)
        self.setStyleSheet(f"""
           QPushButton {{
                background-color: {COLOR_TEAL};
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 4px 8px;;
                border-radius: 20px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {COLOR_MINT};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_SLATE};
            }}
        """)

class StyledDialog(QDialog):
    """
    A reusable QDialog with consistent HR app styling.
    Applies styles to all child widgets: QLabel, QLineEdit, QComboBox, QPushButton.
    """
    def __init__(self, parent=None, title="Dialog"):
        super().__init__(parent)
        self.setWindowTitle(title)

        # Main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Apply stylesheet to all common widgets in this dialog
        self.setStyleSheet(f"""
            QDialog {{
                background-color: rgba(3, 47, 48, 0.95);  /* dark greenish */
                border-radius: 12px;
            }}
            QLabel {{
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}
            QLineEdit, QTextEdit {{
                background-color: {COLOR_DARK_GREEN};
                color: white;
                border: 1px solid {COLOR_TEAL};
                border-radius: 6px;
                padding: 6px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {COLOR_MINT};
            }}
            QComboBox {{
                background-color: {COLOR_DARK_GREEN};
                color: white;
                border: 1px solid {COLOR_TEAL};
                border-radius: 6px;
                padding: 6px;
            }}
            QComboBox:focus {{
                border: 1px solid {COLOR_MINT};
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLOR_DARK_GREEN};
                color: white;
                selection-background-color: {COLOR_TEAL};
                selection-color: white;
                border: 1px solid {COLOR_TEAL};
            }}
            QPushButton {{
                background-color: {COLOR_TEAL};
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_MINT};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_SLATE};
            }}
            QFormLayout {{
                spacing: 10px;
                margin: 15px;
            }}
            QCheckBox {{
                color: white;
                font-size: 13px;
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {COLOR_TEAL};
                background-color: {COLOR_DARK_GREEN};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLOR_TEAL};
                border: 1px solid {COLOR_MINT};
            }}
            QCheckBox::indicator:unchecked:hover {{
                border: 1px solid {COLOR_MINT};
            }}
        """)

        # Optional: shadow for depth
        apply_card_shadow(self)