import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QLineEdit, QLabel, QMessageBox, QDialog, QFormLayout,
    QScrollArea, QDialogButtonBox, QComboBox, QToolButton, QMenu, QInputDialog, QFileDialog
)
from PyQt6.QtCore import Qt
import pandas as pd
from datetime import datetime

class EmployeePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HR Training Tracker")

        # Database setup
        self.conn = sqlite3.connect("hr_app.db")
        self.create_tables()

        # Layout
        self.main_layout = QVBoxLayout()

        # === Scroll Area ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_employees = QPushButton("Refresh Employees")
        self.btn_employees.clicked.connect(self.show_employees)
        btn_layout.addWidget(self.btn_employees)

        self.import_btn = QPushButton("Import Employees")
        self.import_btn.clicked.connect(self.import_employees_from_excel)
        btn_layout.addWidget(self.import_btn)

        self.export_btn = QPushButton("Export Employees")
        self.export_btn.clicked.connect(self.export_employees_to_excel)
        btn_layout.addWidget(self.export_btn)


        self.scroll_layout.addLayout(btn_layout)

        # Table widget
        self.table = QTableWidget()
        self.scroll_layout.addWidget(self.table)

        scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(scroll_area)

       # Floating Add Button
        self.btn_add = QPushButton("+")
        self.btn_add.setFixedSize(60, 60)
        self.btn_add.setStyleSheet("""
            QPushButton {
                border-radius: 30px;
                background-color: #0078d7;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        self.btn_add.clicked.connect(self.add_item_placeholder)  # empty for now

        # Add button stays bottom-right
        self.main_layout.addWidget(
            self.btn_add,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
        )

        self.setLayout(self.main_layout)
        self.show_employees()


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
            description TEXT
        )
        """)
        self.conn.commit()

    def show_employees(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(5)  # Extra column for the button
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Job", "Department", "Details"])

        for col in range(self.table.columnCount()):
            self.table.setColumnWidth(col, self.table.columnWidth(col) + 35)

        # Fill the table
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

            # Add "..." button in last column
            btn = QPushButton("...")
            btn.clicked.connect(lambda checked, emp_id=row[0]: self.show_employee_details(emp_id))
            self.table.setCellWidget(i, 4, btn)

        # === Add down arrow buttons for headers (except Details) ===
        header = self.table.horizontalHeader()
        header.setSectionsClickable(True)

        # Remove old buttons if they exist
        if hasattr(self, "header_buttons"):
            for b in self.header_buttons:
                b.deleteLater()

        self.header_buttons = []

        # Create buttons for first 4 headers
        for col in range(4):
            btn = QToolButton(self.table)
            btn.setText("▼")
            btn.setAutoRaise(True)
            btn.clicked.connect(lambda checked, c=col: self.handle_header_click(c))  # pass column index
            self.header_buttons.append(btn)
            btn.show()

        # Position buttons initially
        self._position_header_buttons()

        # Reposition buttons if columns are resized
        header.sectionResized.connect(lambda idx, old, new: self._position_header_buttons())
        header.sectionMoved.connect(lambda idx, old, new: self._position_header_buttons())

    # Helper method to position buttons
    def _position_header_buttons(self):
        header = self.table.horizontalHeader()
        for col, btn in enumerate(self.header_buttons):
            x = self.table.columnViewportPosition(col) + self.table.columnWidth(col) - 20
            y = 0
            btn.setGeometry(x, y, 20, header.height())

    # Example handler for button clicks
    def handle_header_click(self, col):
        """Show menu with sort/filter options for the given column."""
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
        """Filter rows based on text in the given column."""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, col)
            if item:
                match = text.lower() in item.text().lower()
                self.table.setRowHidden(row, not match)


    def show_employee_details(self, emp_id):
        """Open a dialog showing details of one employee with edit/delete options."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE id=?", (emp_id,))
        employee = cursor.fetchone()

        def loadDept():
                cursor = self.conn.cursor()
                cursor.execute("SELECT name FROM departments ORDER BY name")
                for row in cursor.fetchall():
                    self.dept_edit.addItem(row[0])
                index = self.dept_edit.findText(employee[3])
                if index >= 0:
                    self.dept_edit.setCurrentIndex(index)

        if employee:
            dialog = QDialog(self)
            dialog.setWindowTitle("Employee Details")
            layout = QVBoxLayout()

            # Fields
            form_layout = QFormLayout()
            form_layout.addRow("ID:", QLabel(str(employee[0])))

            # Editable fields
            self.name_label = QLabel(employee[1])
            self.name_edit = QLineEdit(employee[1])
            self.name_edit.hide()
            form_layout.addRow("Name:", self.name_label)
            form_layout.addRow("", self.name_edit)

            self.job_label = QLabel(employee[2])
            self.job_edit = QLineEdit(employee[2])
            self.job_edit.hide()
            form_layout.addRow("Job:", self.job_label)
            form_layout.addRow("", self.job_edit)

            self.dept_label = QLabel(employee[3])
            self.dept_edit = QComboBox()
            loadDept()
            self.dept_edit.hide()
            form_layout.addRow("Department:", self.dept_label)
            form_layout.addRow("", self.dept_edit)

            layout.addLayout(form_layout)

            # Buttons
            btn_layout = QHBoxLayout()
            self.btn_edit = QPushButton("Edit")
            self.btn_delete = QPushButton("Delete")
            self.btn_cancel = QPushButton("Close")

            btn_layout.addWidget(self.btn_edit)
            btn_layout.addWidget(self.btn_delete)
            btn_layout.addWidget(self.btn_cancel)
            layout.addLayout(btn_layout)

            dialog.setLayout(layout)

            # === Button Actions ===
            def toggle_edit():
                if self.btn_edit.text() == "Edit":
                    self.name_label.hide()
                    self.job_label.hide()
                    self.dept_label.hide()

                    self.name_edit.show()
                    self.job_edit.show()
                    self.dept_edit.show()

                    self.btn_edit.setText("Save")
                else:
                    new_name = self.name_edit.text().strip()
                    new_job = self.job_edit.text().strip()
                    new_dept = self.dept_edit.currentText().strip()

                    # Update employee record
                    cursor.execute("""
                        UPDATE employees
                        SET name=?, job=?, department=?
                        WHERE id=?
                    """, (new_name, new_job, new_dept, emp_id))
                    self.conn.commit()

                    # === Update related training tables ===
                    cursor.execute("SELECT id, name, departments FROM trainings")
                    trainings = cursor.fetchall()

                    for t_id, t_name, t_depts in trainings:
                        # Clean training name so it can be used as a table name
                        safe_name = "".join(c if c.isalnum() else "_" for c in t_name)
                        table_name = f"{safe_name}_{t_id}"

                        # If this training applies to the new department
                        if new_dept in (t_depts or ""):
                            cursor.execute(f"SELECT 1 FROM {table_name} WHERE employee_id=?", (emp_id,))
                            if not cursor.fetchone():
                                cursor.execute(
                                    f"INSERT INTO {table_name} (employee_id, status) VALUES (?, ?)",
                                    (emp_id, "Not Started")
                                )
                        else:
                            # Mark as "Not Required" instead of deleting
                            cursor.execute(
                                f"UPDATE {table_name} SET status=? WHERE employee_id=?",
                                ("Not Required", emp_id)
                            )

                    self.conn.commit()

                    # Update UI labels
                    self.name_label.setText(new_name)
                    self.job_label.setText(new_job)
                    self.dept_label.setText(new_dept)

                    self.name_label.show()
                    self.job_label.show()
                    self.dept_label.show()

                    self.name_edit.hide()
                    self.job_edit.hide()
                    self.dept_edit.hide()
                    self.show_employees()

                    self.btn_edit.setText("Edit")


            def delete_employee():
                confirm = QMessageBox.question(
                    dialog,
                    "Confirm Delete",
                    "Are you sure you want to delete this employee?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if confirm == QMessageBox.StandardButton.Yes:
                    # Check all training tables first
                    cursor.execute("SELECT id, name FROM trainings")
                    trainings = cursor.fetchall()

                    for t_id, t_name in trainings:
                        safe_name = "".join(c if c.isalnum() else "_" for c in t_name)
                        table_name = f"{safe_name}_{t_id}"

                        cursor.execute(f"SELECT status FROM {table_name} WHERE employee_id=?", (emp_id,))
                        record = cursor.fetchone()
                        if record:
                            current_status = record[0]
                            if current_status != "Completed":
                                cursor.execute(
                                    f"UPDATE {table_name} SET status=? WHERE employee_id=?",
                                    ("Not Required", emp_id)
                                )

                    self.conn.commit()

                    # Now delete the employee
                    cursor.execute("DELETE FROM employees WHERE id=?", (emp_id,))
                    self.conn.commit()

                    self.show_employees()
                    dialog.accept()  # close dialog


            self.btn_edit.clicked.connect(toggle_edit)
            self.btn_delete.clicked.connect(delete_employee)
            self.btn_cancel.clicked.connect(dialog.reject)

            dialog.exec()

    def add_item_placeholder(self):
        """Open a dialog to add a new employee."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Employee")

        layout = QFormLayout(dialog)

        # Input fields
        name_input = QLineEdit()
        job_input = QLineEdit()
        dept_input = QComboBox()

        def loadDept():
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM departments ORDER BY name")
            for row in cursor.fetchall():
                dept_input.addItem(row[0])

        loadDept()

        layout.addRow("Name:", name_input)
        layout.addRow("Job:", job_input)
        layout.addRow("Department:", dept_input)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addRow(buttons)

        def save_employee():
            name = name_input.text().strip()
            job = job_input.text().strip()
            dept = dept_input.currentText().strip()

            if not name or not job or not dept:
                QMessageBox.warning(dialog, "Error", "All fields must be filled in.")
                return

            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO employees (name, job, department) VALUES (?, ?, ?)",
                (name, job, dept)
            )
            self.conn.commit()

            # Get the new employee's ID
            emp_id = cursor.lastrowid

            # Find all trainings that include this department
            cursor.execute("SELECT id, name, departments FROM trainings")
            trainings = cursor.fetchall()

            for t_id, t_name, t_depts in trainings:
                if dept in (t_depts or ""):
                    # Same sanitisation used for training table name
                    safe_name = "".join(c if c.isalnum() else "_" for c in t_name)
                    table_name = f"{safe_name}_{t_id}"

                    cursor.execute(
                        f"INSERT INTO {table_name} (employee_id, status) VALUES (?, ?)",
                        (emp_id, "Not Started")
                    )

            self.conn.commit()

            QMessageBox.information(dialog, "Success", "Employee added successfully.")
            dialog.accept()
            self.show_employees()  # refresh table

        buttons.accepted.connect(save_employee)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def import_employees_from_excel(self):
        """Import employees from an Excel file into the employees table.

        - Detect header row in first 10 rows (case-insensitive).
        - Require columns: Name, Job, Department.
        - Add missing departments to DB automatically.
        - Skip exact duplicates (same name, job, department).
        - Add employee to any training tables that include their department.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Employee Excel File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if not file_path:
            return  # User cancelled

        try:
            required = {"name", "job", "department"}

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
                    "Could not find required header row (Name, Job, Department) in the first 10 rows."
                )
                return

            # 2) Re-read file with detected header row
            df = pd.read_excel(file_path, header=header_row_index)

            # 3) Map columns case-insensitively
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
            job_col = col_map["job"]
            dept_col = col_map["department"]

            cursor = self.conn.cursor()
            added_count = 0

            # 4) Process each data row
            for _, row in df.iterrows():
                # Safely read values
                name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ""
                job = str(row[job_col]).strip() if pd.notna(row[job_col]) else ""
                dept = str(row[dept_col]).strip() if pd.notna(row[dept_col]) else ""

                if not name or not job or not dept:
                    # skip incomplete rows
                    continue

                # 5) Ensure department exists in departments table (create if missing)
                cursor.execute("SELECT name FROM departments WHERE name=?", (dept,))
                if not cursor.fetchone():
                    try:
                        cursor.execute("INSERT INTO departments (name) VALUES (?)", (dept,))
                    except sqlite3.IntegrityError:
                        # concurrent insert or race — ignore
                        pass

                # 6) Check for duplicate employee (same name, job, department)
                cursor.execute(
                    "SELECT id FROM employees WHERE name=? AND job=? AND department=?",
                    (name, job, dept)
                )
                existing = cursor.fetchone()
                if existing:
                    emp_id = existing[0]
                else:
                    # Insert new employee
                    cursor.execute(
                        "INSERT INTO employees (name, job, department) VALUES (?, ?, ?)",
                        (name, job, dept)
                    )
                    emp_id = cursor.lastrowid
                    added_count += 1

                # 7) Add / ensure in training tables where this department applies
                cursor.execute("SELECT id, name, departments FROM trainings")
                trainings = cursor.fetchall()
                for t_id, t_name, t_depts in trainings:
                    # build normalized list of departments for this training
                    dept_list = []
                    if t_depts and isinstance(t_depts, str):
                        dept_list = [d.strip().lower() for d in t_depts.split(",") if d.strip()]

                    if dept.lower() in dept_list:
                        # sanitize training name for table name
                        safe_name = "".join(c if c.isalnum() else "_" for c in t_name)
                        table_name = f"{safe_name}_{t_id}"

                        # ensure training table exists and has the expected schema
                        cursor.execute(f"""
                            CREATE TABLE IF NOT EXISTS "{table_name}" (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                employee_id INTEGER,
                                employee_name TEXT,
                                department TEXT,
                                completed INTEGER DEFAULT 0
                            )
                        """)

                        # avoid duplicate entry in training table
                        cursor.execute(f'SELECT 1 FROM "{table_name}" WHERE employee_id=?', (emp_id,))
                        if not cursor.fetchone():
                            cursor.execute(
                                f'INSERT INTO "{table_name}" (employee_id, employee_name, department, completed) VALUES (?, ?, ?, ?)',
                                (emp_id, name, dept, 0)
                            )

            # 8) Commit and show message
            self.conn.commit()
            QMessageBox.information(
                self,
                "Import Successful",
                f"Successfully imported {added_count} new employees."
            )

            self.show_employees()  # refresh table view

        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import employees:\n{e}"
            )

    def export_employees_to_excel(self):
        """Export employees table into a new Excel sheet with timestamp in name."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, job, department FROM employees")
            rows = cursor.fetchall()

            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=["ID", "Name", "Job", "Department"])

            # Format timestamp for filename and header
            now = datetime.now()
            filename_time = now.strftime("%y%m%d%H%M")  # YYMMDDHHMM
            header_time = now.strftime("%Y/%m/%d at %H:%M")

            # Ask user where to save
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Employee Excel File",
                f"EmployeeTable_{filename_time}.xlsx",
                "Excel Files (*.xlsx)"
            )

            if not file_path:
                return  # cancelled

            # Create Excel writer
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                # First write header message in a new sheet
                header_df = pd.DataFrame(
                    [[f"Employees exported on {header_time}"]],
                    columns=["Message"]
                )
                header_df.to_excel(writer, sheet_name="EmployeeTable", index=False, header=False)

                # Then append employee data below header
                start_row = len(header_df) + 1
                df.to_excel(writer, sheet_name="EmployeeTable", index=False, startrow=start_row)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Employees exported successfully:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export employees:\n{e}"
            )


