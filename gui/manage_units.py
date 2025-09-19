from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QScrollArea, QGroupBox, QMessageBox,
    QDialog, QListWidget, QListWidgetItem, QAbstractItemView
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import sqlite3
import json
import os

# Helper to create a student card with profile image
def create_student_card(student_id, name):
    card = QWidget()
    layout = QHBoxLayout(card)
    image_label = QLabel()
    image_path = f"students/{student_id}_face.jpg"
    if os.path.exists(image_path):
        pixmap = QPixmap(image_path).scaled(60, 60)
    else:
        pixmap = QPixmap(60, 60)
        pixmap.fill(Qt.GlobalColor.gray)
    image_label.setPixmap(pixmap)
    layout.addWidget(image_label)
    info = QLabel(f"{name}\nID: {student_id}")
    layout.addWidget(info)
    card.setLayout(layout)
    return card


# Removed duplicate/incomplete ManageUnitsWindow class definition

class ManageUnitsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Units")
        self.setGeometry(200, 100, 700, 600)
        # self.setStyleSheet("background-color: #f8f9fa;")

        self.conn = sqlite3.connect("database/students.db")
        self.ensure_units_table()
        self.ensure_student_units_table()
        self.init_ui()

    def ensure_units_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_name TEXT NOT NULL,
                unit_code TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def ensure_student_units_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                unit_id INTEGER
            )
        """)
        self.conn.commit()

    def init_ui(self):
        layout = QVBoxLayout()

        # Form to add unit
        form_layout = QHBoxLayout()
        self.unit_name_input = QLineEdit()
        self.unit_name_input.setPlaceholderText("Unit Name")
        self.unit_code_input = QLineEdit()
        self.unit_code_input.setPlaceholderText("Unit Code")
        add_button = QPushButton("Add Unit")
        add_button.clicked.connect(self.add_unit)
        form_layout.addWidget(self.unit_name_input)
        form_layout.addWidget(self.unit_code_input)
        form_layout.addWidget(add_button)
        layout.addLayout(form_layout)

        # Scroll area for unit cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.unit_container = QWidget()
        self.unit_layout = QVBoxLayout()
        self.unit_container.setLayout(self.unit_layout)
        self.scroll.setWidget(self.unit_container)

        layout.addWidget(self.scroll)
        self.setLayout(layout)
        self.load_units()

    def add_unit(self):
        name = self.unit_name_input.text().strip()
        code = self.unit_code_input.text().strip()

        if not name or not code:
            QMessageBox.warning(
                self,
                "Input Error",
                "Please enter both name and code."
            )
            return

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO units (unit_name, unit_code) VALUES (?, ?)",
            (name, code)
        )
        self.conn.commit()
        QMessageBox.information(
            self,
            "Unit Added",
            f"{name} added successfully."
        )
        self.unit_name_input.clear()
        self.unit_code_input.clear()
        self.load_units()

    def load_units(self):
        for i in reversed(range(self.unit_layout.count())):
            item = self.unit_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget:
                    widget.setParent(None)

        cursor = self.conn.cursor()
        cursor.execute("SELECT id, unit_name, unit_code FROM units")
        for unit_id, name, code in cursor.fetchall():
            box = QGroupBox()
            box.setStyleSheet(
                "QGroupBox {"
                " border: 1px solid #ccc;"
                " border-radius: 8px;"
                " padding: 10px;"
                " }"
            )
            inner = QVBoxLayout()

            title = QLabel(f"{name} ({code})")
            title.setFont(QFont("Segoe UI", 14, QFont.Bold))
            inner.addWidget(title)

            btn_row = QHBoxLayout()
            assign_btn = QPushButton("👥 Assign Students")
            assign_btn.clicked.connect(
                lambda checked, uid=unit_id: self.assign_students(uid)
            )
            init_btn = QPushButton("✅ Set Active")
            init_btn.clicked.connect(
                lambda checked, uid=unit_id: self.set_active_unit(uid)
            )
            view_btn = QPushButton("👁 View Students")
            view_btn.clicked.connect(
                lambda checked, uid=unit_id: self.view_students(uid)
            )
            prepare_btn = QPushButton("🛡️ Prepare for Attendance")
            prepare_btn.clicked.connect(lambda checked, uid=unit_id: self.prepare_for_attendance(uid, name, code))
            btn_row.addWidget(assign_btn)
            btn_row.addWidget(init_btn)
            btn_row.addWidget(view_btn)
            btn_row.addWidget(prepare_btn)

            inner.addLayout(btn_row)
            box.setLayout(inner)
            self.unit_layout.addWidget(box)

        self.unit_layout.addStretch()

    def prepare_for_attendance(self, unit_id, unit_name, unit_code):
        import random, string, json
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog
        from PyQt5.QtGui import QIcon, QFont, QGuiApplication
        password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        with open("active_unit.json", "w") as f:
            json.dump({"unit_id": unit_id, "unit_name": unit_name, "unit_code": unit_code, "password": password}, f)

        dialog = QDialog(self)
        dialog.setWindowTitle("Attendance Prepared")
        layout = QVBoxLayout()
        info_label = QLabel(f"<b>Unit:</b> <span style='color:#007bff'>{unit_name} ({unit_code})</span>")
        info_label.setFont(QFont("Segoe UI", 14))
        layout.addWidget(info_label)
        layout.addSpacing(10)
        pass_label = QLabel(f"<b>Password:</b> <span style='color:#28a745; font-size:18px;'>{password}</span>")
        pass_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(pass_label)
        layout.addSpacing(10)
        instruct = QLabel("Share this password with the lecturer to start attendance.")
        instruct.setStyleSheet("color: #6c757d; font-size:13px;")
        layout.addWidget(instruct)
        layout.addSpacing(15)

        btn_row = QHBoxLayout()
        copy_btn = QPushButton("Copy Password")
        copy_btn.setIcon(QIcon.fromTheme("edit-copy"))
        copy_btn.setStyleSheet("padding: 8px; border-radius: 6px;")
        def copy_password():
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(password)
        copy_btn.clicked.connect(copy_password)
        btn_row.addWidget(copy_btn)

        download_btn = QPushButton("Download Password")
        download_btn.setIcon(QIcon.fromTheme("document-save"))
        download_btn.setStyleSheet("padding: 8px; border-radius: 6px;")
        def download_password():
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(dialog, "Save Password", "unit_password.txt", "Text Files (*.txt);;All Files (*)", options=options)
            if file_path:
                with open(file_path, "w") as f:
                    f.write(f"Unit: {unit_name} ({unit_code})\nPassword: {password}\n")
        download_btn.clicked.connect(download_password)
        btn_row.addWidget(download_btn)

        layout.addLayout(btn_row)
        layout.addSpacing(20)
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("padding: 8px; border-radius: 6px;")
        close_btn.setIcon(QIcon.fromTheme("window-close"))
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def assign_students(self, unit_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Assign Students to Unit")
        dialog.setMinimumSize(400, 400)

        layout = QVBoxLayout()
        label = QLabel("Select students for this unit:")
        layout.addWidget(label)

        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.MultiSelection)

        cursor = self.conn.cursor()
        cursor.execute("SELECT student_id, name FROM students")
        all_students = cursor.fetchall()

        # Fetch already assigned students
        cursor.execute(
            "SELECT student_id FROM student_units WHERE unit_id = ?",
            (unit_id,)
        )
        assigned_ids = {sid[0] for sid in cursor.fetchall()}

        for sid, name in all_students:
            item_widget = create_student_card(sid, name)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, sid)
            item.setSelected(sid in assigned_ids)
            list_widget.addItem(item)
            list_widget.setItemWidget(item, item_widget)

        layout.addWidget(list_widget)

        save_btn = QPushButton("Save")

        def save_students():
            self.save_assigned_students(dialog, unit_id, list_widget)
        save_btn.clicked.connect(save_students)
        layout.addWidget(save_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def save_assigned_students(self, dialog, unit_id, list_widget):
        selected_students = [
            item.data(Qt.ItemDataRole.UserRole)
            for item in list_widget.selectedItems()
        ]
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM student_units WHERE unit_id = ?",
            (unit_id,)
        )
        for sid in selected_students:
            cursor.execute(
                (
                    "INSERT INTO student_units "
                    "(student_id, unit_id) VALUES (?, ?)"
                ),
                (sid, unit_id)
            )
        self.conn.commit()
        QMessageBox.information(self, "Saved", "Student assignments updated.")
        dialog.close()

    def view_students(self, unit_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Students in This Unit")
        dialog.setMinimumSize(400, 400)

        layout = QVBoxLayout()
        label = QLabel("List of students assigned:")
        layout.addWidget(label)

        list_widget = QListWidget()
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT students.student_id, students.name
            FROM students
            JOIN student_units
                ON students.student_id = student_units.student_id
            WHERE student_units.unit_id = ?
            """,
            (unit_id,)
        )

        for sid, name in cursor.fetchall():
            item_widget = create_student_card(sid, name)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            list_widget.addItem(item)
            list_widget.setItemWidget(item, item_widget)

        layout.addWidget(list_widget)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def set_active_unit(self, unit_id):
        with open("active_unit.json", "w") as f:
            json.dump({"unit_id": unit_id}, f)
        QMessageBox.information(
            self,
            "Set Active",
            (
                f"Unit ID {unit_id} is now active for attendance."
            )
        )

    # Removed duplicate closeEvent method to resolve
    # obscured declaration error.

    # Removed duplicate assign_students method to resolve
    # obscured declaration error.
    def view_unit_students(self, unit_id):
        dlg = QWidget()
        dlg.setWindowTitle("Students in Unit")
        dlg.setGeometry(350, 250, 400, 500)
        vbox = QVBoxLayout(dlg)

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.student_id, s.name FROM students s
            JOIN student_units su ON s.student_id = su.student_id
            WHERE su.unit_id=?
        """, (unit_id,))
        students = cursor.fetchall()

        label = QLabel("Students registered for this unit:")
        vbox.addWidget(label)

        for sid, name in students:
            vbox.addWidget(QLabel(f"{name} ({sid})"))

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        vbox.addWidget(close_btn)
        dlg.show()

    def closeEvent(self, a0):
        self.conn.close()
        super().closeEvent(a0)
