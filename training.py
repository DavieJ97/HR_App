import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QLineEdit, QLabel, QMessageBox, QDialog, QFormLayout,
    QScrollArea, QDialogButtonBox, QTextEdit, QCheckBox, QFileDialog
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
from employee_trainings import EmployeeTrainingPages
import pandas as pd
from datetime import datetime
import objects

class TrainingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HR Training Tracker")
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
        self.create_tables()

        # Layout
        self.main_layout = QVBoxLayout()

        btn_frame = objects.ButtonFrame()

        # Buttons
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setSpacing(15)
        self.btn_trainings = objects.StyledButton("Refresh Trainings")
        self.btn_trainings.setIcon(QIcon("icons/refresh.png"))
        self.btn_trainings.setIconSize(QSize(32, 32))
        self.btn_trainings.clicked.connect(self.show_trainings)
        btn_layout.addWidget(self.btn_trainings)

        self.import_trainings = objects.StyledButton("Upload Trainings")
        self.import_trainings.setIcon(QIcon("icons/upload.png"))
        self.import_trainings.setIconSize(QSize(32, 32))
        self.import_trainings.clicked.connect(self.import_trainings_from_excel)
        btn_layout.addWidget(self.import_trainings)

        self.export_trainings = objects.StyledButton("Download Trainings")
        self.export_trainings.setIcon(QIcon("icons/download.png"))
        self.export_trainings.setIconSize(QSize(32, 32))
        self.export_trainings.clicked.connect(self.export_trainings_to_excel)
        btn_layout.addWidget(self.export_trainings)

        # === Scroll Area ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        self.scroll_layout.addWidget(btn_frame)

        # Table widget
        self.table = objects.Table()
        self.scroll_layout.addWidget(self.table)

        scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(scroll_area)

       # Floating Add Button
        self.btn_add = objects.FloatingButton("")
        self.btn_add.setIcon(QIcon("icons/new.png"))
        self.btn_add.setIconSize(QSize(32, 32))
        self.btn_add.clicked.connect(self.add_item_placeholder)  # empty for now

        # Add button stays bottom-right
        self.main_layout.addWidget(
            self.btn_add,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
        )

        self.setLayout(self.main_layout)

        self.show_trainings()


    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            job TEXT,
            department TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trainings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            departments TEXT
        )
        """)
        self.conn.commit()


    def show_trainings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM trainings")
        rows = cursor.fetchall()

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(6)  # Extra column for button
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Description", "Departments", "Details", "Employees"])

        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

            # Add "..." button in second last column and view to the last
            detail_btn = objects.TableStyledButton("...")
            detail_btn.clicked.connect(lambda checked, training_id=row[0]: self.show_training_details(training_id))
            self.table.setCellWidget(i, 4, detail_btn)
            emp_btn = objects.TableStyledButton("View")
            emp_btn.clicked.connect(lambda checked, training_id=row[0], training_name=row[1]: self.openEmployeeTrainings(training_id, training_name))
            self.table.setCellWidget(i, 5, emp_btn)


    def show_training_details(self, training_id):
        """Open a dialog showing details of one training with edit/delete options."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM trainings WHERE id=?", (training_id,))
        training = cursor.fetchone()

        if training:
            dialog = objects.StyledDialog(self, "Training Details")

            # Fields
            form_layout = QFormLayout()
            dialog.main_layout.addLayout(form_layout)
            form_layout.addRow("ID:", QLabel(str(training[0])))
            form_layout.addRow("Name:", QLabel(training[1]))

            # Description
            self.desc_label = QLabel(training[2])
            self.desc_edit = QTextEdit(training[2])
            self.desc_edit.hide()
            form_layout.addRow("Description:", self.desc_label)
            form_layout.addRow("", self.desc_edit)

            # === Departments ===
            self.dept_label = QLabel(training[3] if len(training) > 3 and training[3] else "")
            self.dept_box = QWidget()
            dept_layout = QVBoxLayout(self.dept_box)

            cursor.execute("SELECT name FROM departments ORDER BY name")
            dept_checks = []
            existing_depts = (training[3] or "").split(", ")
            for row in cursor.fetchall():
                chk = QCheckBox(row[0])
                if row[0] in existing_depts:
                    chk.setChecked(True)
                dept_layout.addWidget(chk)
                dept_checks.append(chk)
            self.dept_box.hide()

            form_layout.addRow("Departments:", self.dept_label)
            form_layout.addRow("", self.dept_box)


            # Buttons
            btn_layout = QHBoxLayout()
            self.btn_edit = QPushButton("Edit")
            self.btn_delete = QPushButton("Delete")
            self.btn_cancel = QPushButton("Close")

            btn_layout.addWidget(self.btn_edit)
            btn_layout.addWidget(self.btn_delete)
            btn_layout.addWidget(self.btn_cancel)
            dialog.main_layout.addLayout(btn_layout)

            # === Button Actions ===
            def toggle_edit():
                if self.btn_edit.text() == "Edit":
                    self.desc_label.hide()
                    self.desc_edit.show()
                    self.dept_label.hide()
                    self.dept_box.show()
                    self.btn_edit.setText("Save")
                else:
                    new_desc = self.desc_edit.toPlainText()
                    selected_depts = [chk.text() for chk in dept_checks if chk.isChecked()]
                    dept_string = ", ".join(selected_depts)
                    cursor.execute(
                        "UPDATE trainings SET description=?, departments=? WHERE id=?",
                        (new_desc, dept_string, training_id)
                    )
                    self.conn.commit()
                    self.show_trainings()
                    self.desc_label.setText(new_desc)
                    self.desc_label.show()
                    self.desc_edit.hide()
                    self.dept_label.setText(dept_string)
                    self.dept_label.show()
                    self.dept_box.hide()
                    self.btn_edit.setText("Edit")

            def delete_training():
                confirm = QMessageBox.question(dialog, "Confirm Delete",
                                               "Are you sure you want to delete this training?",
                                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if confirm == QMessageBox.StandardButton.Yes:
                    cursor.execute("DELETE FROM trainings WHERE id=?", (training_id,))
                    self.conn.commit()
                    self.show_trainings()
                    dialog.accept()  # close dialog

            self.btn_edit.clicked.connect(toggle_edit)
            self.btn_delete.clicked.connect(delete_training)
            self.btn_cancel.clicked.connect(dialog.reject)

            dialog.exec()

    
    def add_item_placeholder(self):
        """Open dialog to add a new training and save it to the database."""
        dialog = objects.StyledDialog(self, "Add Training")

        layout = QFormLayout()
        dialog.main_layout.addLayout(layout)

        # Input fields
        name_input = QLineEdit()
        desc_input = QTextEdit()
        desc_input.setFixedHeight(100)

        dept_box = QWidget()
        dept_layout = QVBoxLayout(dept_box)

        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM departments ORDER BY name")
        dept_checks = []
        for row in cursor.fetchall():
            chk = QCheckBox(row[0])
            dept_layout.addWidget(chk)
            dept_checks.append(chk)
        layout.addRow("Training Name:", name_input)
        layout.addRow("Description:", desc_input)
        layout.addRow("Departments:", dept_box)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        dialog.main_layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec():
            name = name_input.text().strip().replace(" ", "_")  # ensure safe table name
            desc = desc_input.toPlainText().strip()
            selected_depts = [chk.text() for chk in dept_checks if chk.isChecked()]
            dept_string = ", ".join(selected_depts)

            if name:
                cursor = self.conn.cursor()
                # 1. Save the training to the trainings table
                cursor.execute(
                    "INSERT INTO trainings (name, description, departments) VALUES (?, ?, ?)",
                    (name, desc, dept_string)
                )
                self.conn.commit()

                # Get the new training's ID
                training_id = cursor.lastrowid
                table_name = f"{name}_{training_id}"

                # 2. Create a new table for this training
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER,
                        employee_name TEXT,
                        department TEXT,
                        completed INTEGER DEFAULT 0,
                        FOREIGN KEY (employee_id) REFERENCES employees(id)
                    )
                """)

                # 3. Add employees from the selected departments into the new table
                for dept in selected_depts:
                    cursor.execute("SELECT id, name, department FROM employees WHERE department = ?", (dept,))
                    employees = cursor.fetchall()
                    for emp in employees:
                        cursor.execute(
                            f"INSERT INTO {table_name} (employee_id, employee_name, department, completed) VALUES (?, ?, ?, ?)",
                            (emp[0], emp[1], emp[2], 0)
                        )

                self.conn.commit()
                self.show_trainings()  # Refresh table

    def openEmployeeTrainings(self, training_id, training_name):
        self.training_page = EmployeeTrainingPages()
        self.training_page.showMaximized()
        self.training_page.show_training_employees(training_id, training_name)
        self.training_page.show()
    
    def import_trainings_from_excel(self):
        """Import trainings from an Excel file into the trainings table.

        - Detect header row in first 10 rows (case-insensitive).
        - Required columns: Name, Description, Departments.
        - If a training name already exists (case-insensitive), update its record.
        - Ensure training table exists and add missing employees from the listed departments.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Trainings Excel File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return

        try:
            required = {"name", "description", "departments"}

            # 1) Preview first 10 rows (no header) to find header row
            preview = pd.read_excel(file_path, header=None, nrows=10)
            header_row_index = None
            for i, row in preview.iterrows():
                row_vals = [str(v).strip().lower() for v in row.values if pd.notna(v)]
                if required.issubset(set(row_vals)):
                    header_row_index = i
                    break

            if header_row_index is None:
                QMessageBox.warning(
                    self,
                    "Invalid File",
                    "Could not find required header row (Name, Description, Departments) in the first 10 rows."
                )
                return

            # 2) Re-read file with detected header row
            df = pd.read_excel(file_path, header=header_row_index)
            # normalize column names
            df.columns = [str(c).strip() for c in df.columns]
            col_map = {str(c).strip().lower(): c for c in df.columns}
            missing = required - set(col_map.keys())
            if missing:
                QMessageBox.warning(
                    self,
                    "Invalid File",
                    f"Missing required columns after header detection: {', '.join(missing)}"
                )
                return

            name_col = col_map["name"]
            desc_col = col_map["description"]
            depts_col = col_map["departments"]

            cursor = self.conn.cursor()
            added_count = 0
            updated_count = 0

            for _, row in df.iterrows():
                raw_name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ""
                if not raw_name:
                    continue
                # keep stored name consistent with previous code: replace spaces with underscore
                stored_name = raw_name.replace(" ", "_")
                desc = str(row[desc_col]).strip() if pd.notna(row[desc_col]) else ""
                depts = str(row[depts_col]).strip() if pd.notna(row[depts_col]) else ""

                if not stored_name or not desc or not depts:
                    continue  # skip incomplete rows

                # 3) Check for existing training by name (case-insensitive)
                cursor.execute("SELECT id, name, description, departments FROM trainings WHERE LOWER(name)=?", (stored_name.lower(),))
                existing = cursor.fetchone()
                if existing:
                    training_id = existing[0]
                    # update description/departments if changed
                    cursor.execute("UPDATE trainings SET description=?, departments=? WHERE id=?", (desc, depts, training_id))
                    updated_count += 1
                else:
                    # insert new training
                    cursor.execute(
                        "INSERT INTO trainings (name, description, departments) VALUES (?, ?, ?)",
                        (stored_name, desc, depts)
                    )
                    training_id = cursor.lastrowid
                    added_count += 1

                # 4) Create/ensure training table exists (use safe name)
                safe_name = "".join(c if c.isalnum() else "_" for c in stored_name)
                table_name = f"{safe_name}_{training_id}"
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS "{table_name}" (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER,
                        employee_name TEXT,
                        department TEXT,
                        completed INTEGER DEFAULT 0
                    )
                """)

                # 5) Add employees for departments listed (avoid duplicates)
                dept_list = [d.strip() for d in depts.split(",") if d.strip()]
                for dept in dept_list:
                    cursor.execute("SELECT id, name, department FROM employees WHERE department = ?", (dept,))
                    employees = cursor.fetchall()
                    for emp in employees:
                        emp_id, emp_name, emp_dept = emp
                        # avoid duplicate entry in training table
                        cursor.execute(f'SELECT 1 FROM "{table_name}" WHERE employee_id=?', (emp_id,))
                        if not cursor.fetchone():
                            cursor.execute(
                                f'INSERT INTO "{table_name}" (employee_id, employee_name, department, completed) VALUES (?, ?, ?, ?)',
                                (emp_id, emp_name, emp_dept, 0)
                            )

            self.conn.commit()

            QMessageBox.information(
                self,
                "Import Complete",
                f"Imported {added_count} new trainings. Updated {updated_count} existing trainings."
            )
            self.show_trainings()

        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import trainings:\n{e}")



    def export_trainings_to_excel(self):
        """Export all trainings to an Excel file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Trainings Excel File",
            f"TrainingTable_{datetime.now().strftime('%y%m%d%H%M')}.xlsx",
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, description, departments FROM trainings")
            rows = cursor.fetchall()


            df = pd.DataFrame(rows, columns=["ID", "Name", "Description", "Departments"])

            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Trainings", index=False, startrow=2)
                ws = writer.sheets["Trainings"]
                ws.cell(row=1, column=1).value = f"Trainings exported on {datetime.now().strftime('%Y/%m/%d at %H:%M')}"

            QMessageBox.information(self, "Export Successful", f"Trainings exported to:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export trainings:\n{e}")

