import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QScrollArea, QToolButton, QMenu, QInputDialog, QFileDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import pandas as pd
from datetime import datetime
import objects

class EmployeeTrainingPages(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Training Records")
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {objects.COLOR_DARK_GREEN}, stop:0.5 {objects.COLOR_TEAL}, stop:1 {objects.COLOR_MINT}
                );
                font-family: Segoe UI, Arial, sans-serif;
            }}
        """)

        # Database setup
        self.conn = sqlite3.connect("hr_app.db")

        # Layout
        self.main_layout = QVBoxLayout()

        self.header = objects.HeaderLabel("TableName")
        self.main_layout.addWidget(self.header)

        # === Scroll Area ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        # Table widget
        self.table = objects.Table()
        self.scroll_layout.addWidget(self.table)

        scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(scroll_area)

        self.export_btn = objects.FloatingButton("")
        self.export_btn.setIcon(QIcon("icons/download.png"))  # system icon fallback
        self.export_btn.setIconSize(QSize(32, 32))
        self.export_btn.clicked.connect(self.export_training_employees_to_excel)
        self.main_layout.addWidget(self.export_btn, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.setLayout(self.main_layout)

    def show_training_employees(self, training_id, training_name):
        """Show all employees and their status for a given training."""
        cursor = self.conn.cursor()
        self.header.setText(training_name)
        # Safe table name
        safe_name = "".join(c if c.isalnum() else "_" for c in training_name)
        self.table_name = f"{safe_name}_{training_id}"

        # Join training table with employees to get employee names
        cursor.execute(f"""
            SELECT id, employee_id, employee_name, department, status
            FROM "{self.table_name}"
        """)
        rows = cursor.fetchall()

        # Add an extra column for the button
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Employee ID", "Name", "Department", "Status", "Action"])
        
        for col in range(self.table.columnCount()):
            self.table.setColumnWidth(col, self.table.columnWidth(col) + 35)

        for i, row in enumerate(rows):
            db_id, emp_id, name, dept, status = row

            # Fill normal columns
            self.table.setItem(i, 0, QTableWidgetItem(str(db_id)))
            self.table.setItem(i, 1, QTableWidgetItem(str(emp_id)))
            self.table.setItem(i, 2, QTableWidgetItem(name))
            self.table.setItem(i, 3, QTableWidgetItem(dept))
            self.table.setItem(i, 4, QTableWidgetItem(status))

            # Add action button
            btn = objects.TableStyledButton("Toggle")
            btn.clicked.connect(lambda checked, emp_db_id=db_id, row_index=i: self.toggle_training_status(emp_db_id, row_index))
            self.table.setCellWidget(i, 5, btn)

        # === Add down arrow buttons for headers ===
        header = self.table.horizontalHeader()
        header.setSectionsClickable(True)

        # Remove old buttons if they exist
        if hasattr(self, "header_buttons"):
            for b in self.header_buttons:
                b.deleteLater()

        self.header_buttons = []

        for col in range(5):  # now includes Action column
            btn = QToolButton(self.table)
            btn.setText("▼")
            btn.setAutoRaise(True)
            btn.clicked.connect(lambda checked, c=col: self.handle_header_click(c))
            self.header_buttons.append(btn)
            btn.show()

        self._position_header_buttons()
        header.sectionResized.connect(lambda idx, old, new: self._position_header_buttons())
        header.sectionMoved.connect(lambda idx, old, new: self._position_header_buttons())

    # Position buttons
    def _position_header_buttons(self):
        header = self.table.horizontalHeader()
        for col, btn in enumerate(self.header_buttons):
            x = self.table.columnViewportPosition(col) + self.table.columnWidth(col) - 20
            y = 0
            btn.setGeometry(x, y, 20, header.height())

    # Dropdown filter/sort
    def handle_header_click(self, col):
        menu = QMenu(self)

        sort_asc = menu.addAction("Sort Ascending")
        sort_desc = menu.addAction("Sort Descending")
        filter_action = menu.addAction("Filter/Search")

        action = menu.exec(self.header_buttons[col].mapToGlobal(self.header_buttons[col].rect().bottomLeft()))

        if action == sort_asc:
            self.table.sortItems(col, Qt.SortOrder.AscendingOrder)
        elif action == sort_desc:
            self.table.sortItems(col, Qt.SortOrder.DescendingOrder)
        elif action == filter_action:
            text, ok = QInputDialog.getText(self, "Filter", f"Enter text to filter '{self.table.horizontalHeaderItem(col).text()}':")
            if ok:
                self.apply_filter(col, text.strip())

    def apply_filter(self, col, text):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, col)
            if item:
                match = text.lower() in item.text().lower()
                self.table.setRowHidden(row, not match)

    def export_training_employees_to_excel(self):
        """Export all trainings to an Excel file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Trainings Excel File",
            f"{self.table_name}_{datetime.now().strftime('%y%m%d%H%M')}.xlsx",
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT id, employee_id, employee_name, department, status FROM {self.table_name}")
            rows = cursor.fetchall()

            if not rows:
                QMessageBox.information(self, "No Data", "There are no Employees doing this training.")
                return

            df = pd.DataFrame(rows, columns=["ID","Employee ID", "Name", "Departments", "Status"])

            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Trainings", index=False, startrow=2)
                ws = writer.sheets["Trainings"]
                ws.cell(row=1, column=1).value = f"{self.table_name} Trainings exported on {datetime.now().strftime('%Y/%m/%d at %H:%M')}"

            QMessageBox.information(self, "Export Successful", f"Trainings exported to:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export trainings:\n{e}") 

    def toggle_training_status(self, emp_db_id, row_index):
        """Toggle training status (0=Pending, 1=Completed) for a single employee."""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT status FROM {self.table_name} WHERE id=?", (emp_db_id,))
        current_status = cursor.fetchone()[0]

        new_status = "Pending"if current_status == "Completed" else "Completed"
        cursor.execute(f"UPDATE {self.table_name} SET status=? WHERE id=?", (new_status, emp_db_id))
        self.conn.commit()

        # Update UI immediately
        self.table.setItem(row_index, 4, QTableWidgetItem(new_status))
